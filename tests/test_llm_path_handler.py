import pytest
from openai.types.beta.threads import message

from conversation import context_window_manager
from conversation.context_window_manager import ContextWindowManager
from conversation.history import ConversationHistory
from handlers.llm_path_handler import LLMPathHandler
from llm import mock_llm_client
from llm.base_llm_client import BaseLLMClient
from llm.mock_llm_client import MockLLMClient
from prompt import prompt_builder
from prompt.prompt_builder import PromptBuilder
from schemas import MessageRole, LLMMessage, LLMResult, ToolCall
from tool_registry import ToolRegistry
from workflow_practice.test_step_reference import tool_registry


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

class RecordingLLMClient(MockLLMClient):

    def __init__(self):
        super().__init__()
        self.received_messages = []

    def chat(self, messages: list[LLMMessage]) -> LLMResult:
        self.received_messages = list(messages)

        return super().chat(messages)
def test_llm_path_handler_trims_history():
    # 1. 创建 MockLLMClient
    mock_llm_client=RecordingLLMClient()
    # 2. 创建 ConversationHistory
    conversation_history=ConversationHistory(max_messages=20)
    # 3. 预先添加三条历史消息
    message=LLMMessage(
        role=MessageRole.USER,
        content="消息一一"
    )
    message1 = LLMMessage(
        role=MessageRole.ASSISTANT,
        content="消息二二"
    )
    message2 = LLMMessage(
        role=MessageRole.USER,
        content="消息三三"
    )
    conversation_history.add_message("user_001",message)
    conversation_history.add_message("user_001", message1)
    conversation_history.add_message("user_001", message2)
    # 4. 创建 ContextWindowManager(max_tokens=4)
    context_window_manager=FixedBudgetContextWindowManager()
    # 5. 创建 LLMPathHandler 并注入管理器
    prompt_builder=PromptBuilder()
    tool_registry=ToolRegistry()
    llm_path_handler=LLMPathHandler(
        llm_client=mock_llm_client,
        prompt_builder=prompt_builder,
        tool_registry=tool_registry,
        conversation_history=conversation_history,
        context_window_manager=context_window_manager
    )

    # 6. 调用 handle()
    llm_path_handler.handle("你知道我叫什么名字吗","user_001","聊天")
    # 7. 验证 LLM 收到的消息
    assert context_window_manager.calculate_called is True
    assert context_window_manager.received_budget == 4
    contents=[
        message.content
        for message in mock_llm_client.received_messages
    ]
    assert "消息一一" not in contents
    assert "消息二二" in contents
    assert "消息三三" in contents
    assert "你知道我叫什么名字吗" in contents
    assert mock_llm_client.received_messages[0].role == MessageRole.SYSTEM
class FixedBudgetContextWindowManager(ContextWindowManager):

    def __init__(self):
        super().__init__(max_tokens=1000)
        self.calculate_called = False
        self.received_budget = None

    def calculate_history_budget(
        self,
        model_context_limit: int,
        system_tokens: int,
        user_tokens: int,
        reserved_tokens: int
    ) -> int:
        self.calculate_called = True
        return 4

    def trim_history(
            self,
            history_messages: list[LLMMessage],
            max_tokens: int | None = None
    ) -> list[LLMMessage]:
        self.received_budget = max_tokens

        return super().trim_history(
            history_messages,
            max_tokens=max_tokens
        )