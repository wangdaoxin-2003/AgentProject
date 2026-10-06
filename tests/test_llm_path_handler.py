import pytest
from conversation.history import ConversationHistory
from handlers.llm_path_handler import LLMPathHandler
from llm.base_llm_client import BaseLLMClient
from llm.mock_llm_client import MockLLMClient
from prompt.prompt_builder import PromptBuilder
from schemas import MessageRole, LLMMessage, LLMResult, ToolCall
from tool_registry import ToolRegistry


class ToolNotFoundLLMClient(BaseLLMClient):

    def chat(self, messages: list[LLMMessage]) -> LLMResult:
        return LLMResult(
            model="tool-not-found-mock",
            success=True,
            data={
                "content": ""
            },
            tool_calls=[
                ToolCall(
                    id="call_not_found_001",
                    name="nonexistent_tool",
                    arguments={}
                )
            ],
            usage=None,
            error=None
        )


class FailingLLMClient(BaseLLMClient):

    def chat(self, messages: list[LLMMessage]) -> LLMResult:
        return LLMResult(
            model="failing-mock",
            success=False,
            data=None,
            tool_calls=[],
            usage=None,
            error="模拟LLM调用失败"
        )

class AlwaysToolCallLLMClient(BaseLLMClient):

    def chat(self, messages: list[LLMMessage]) -> LLMResult:
        return LLMResult(
            model="always-tool-call-mock",
            success=True,
            data={
                "content": ""
            },
            tool_calls=[
                ToolCall(
                    id="call_always_001",
                    name="calculator",
                    arguments={
                        "expression": "1+1"
                    }
                )
            ],
            usage=None,
            error=None
        )

@pytest.fixture
def handler():
    llm_client = MockLLMClient()
    prompt_builder = PromptBuilder()
    conversation_history = ConversationHistory()
    tool_registry = ToolRegistry()
    return LLMPathHandler(
        llm_client=llm_client,
        prompt_builder=prompt_builder,
        conversation_history=conversation_history,
        tool_registry=tool_registry
    )
def test_single_tool_call(handler):#LLM → Tool → LLM 完整闭环

    response = handler.handle(
        message="计算100+200",
        user_id="test_user_001",
        intent="chat"
    )
    assert response.status == "success"

def test_normal_llm_response(handler):#LLM 不调用工具时正常回答

    response = handler.handle(
        message="你好",
        user_id="test_user_002",
        intent="chat"
    )
    assert response.status =="success"

def test_tool_failure(handler):#Tool 业务失败后仍交给 LLM 继续处理
    response = handler.handle(
        message="计算10/0",
        user_id="test_user_003",
        intent="chat"
    )
    assert  response.status=="success"

def test_conversation_history(handler):#一轮完成后正确保存 User + Assistant
    user_id = "history_user_001"

    handler.handle(
        message="你好",
        user_id=user_id,
        intent="chat"
    )

    history = handler.conversation_history.get_history(
        user_id=user_id
    )

    assert len(history) == 2
    assert history[0].role == MessageRole.USER
    assert history[0].content == "你好"

    assert history[1].role == MessageRole.ASSISTANT
    assert history[1].content == "这是 Mock LLM收到消息：你好"

def test_user_history_isolation(handler):#不同 user_id 的历史互相隔离
    handler.handle(
        message="我是用户A",
        user_id="user_A",
        intent="chat"
    )

    handler.handle(
        message="我是用户B",
        user_id="user_B",
        intent="chat"
    )

    history_a = handler.conversation_history.get_history(
        user_id="user_A"
    )

    history_b = handler.conversation_history.get_history(
        user_id="user_B"
    )

    assert len(history_a) == 2
    assert len(history_b) == 2
    assert history_a[0].content == "我是用户A"
    assert history_b[0].content == "我是用户B"

def test_llm_failure():#LLM 调用失败时 Agent 正确失败
    llm_client = FailingLLMClient()
    prompt_builder = PromptBuilder()
    conversation_history = ConversationHistory()
    tool_registry = ToolRegistry()

    handler = LLMPathHandler(
        llm_client=llm_client,
        prompt_builder=prompt_builder,
        conversation_history=conversation_history,
        tool_registry=tool_registry
    )

    response = handler.handle(
        message="你好",
        user_id="test_user_failure",
        intent="chat"
    )

    assert response.status == "failed"
    assert response.error == "模拟LLM调用失败"


def test_tool_not_found():#模型请求不存在的 Tool 时安全终止
    llm_client = ToolNotFoundLLMClient()
    prompt_builder = PromptBuilder()
    conversation_history = ConversationHistory()
    tool_registry = ToolRegistry()

    handler = LLMPathHandler(
        llm_client=llm_client,
        prompt_builder=prompt_builder,
        conversation_history=conversation_history,
        tool_registry=tool_registry
    )

    response = handler.handle(
        message="测试不存在的工具",
        user_id="test_user_tool_not_found",
        intent="chat"
    )

    assert response.status == "failed"
    assert response.error == "工具不存在：nonexistent_tool"

def test_max_iterations():#模型不断调用 Tool 时 Runtime 强制停止
    llm_client = AlwaysToolCallLLMClient()
    prompt_builder = PromptBuilder()
    conversation_history = ConversationHistory()
    tool_registry = ToolRegistry()

    handler = LLMPathHandler(
        llm_client=llm_client,
        prompt_builder=prompt_builder,
        conversation_history=conversation_history,
        tool_registry=tool_registry
    )

    response = handler.handle(
        message="测试最大循环次数",
        user_id="test_user_max_iterations",
        intent="chat"
    )

    assert response.status == "failed"

