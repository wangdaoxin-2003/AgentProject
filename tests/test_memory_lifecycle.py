from container import ApplicationContainer
from conversation.history import ConversationHistory
from handlers.llm_path_handler import LLMPathHandler
from llm.base_llm_client import BaseLLMClient
from llm.mock_llm_client import MockLLMClient
from path_selector import PathType
from prompt.prompt_builder import PromptBuilder
from schemas import LLMMessage, MessageRole, LLMResult
from tool_registry import ToolRegistry


def test_multi_user_isolation():
    # 1.创建同一个History实例
    history = ConversationHistory()
    # 2.分别保存两个用户的消息
    history.add_message(
        "user001",
        LLMMessage(
            role=MessageRole.USER,
            content="我是用户user001"
        )
    )
    history.add_message(
        "user002",
        LLMMessage(
            role=MessageRole.USER,
            content="我是用户user002"
        )
    )
    user1_history = history.get_history("user001")
    user2_history = history.get_history("user002")

    assert len(user1_history) == 1
    assert len(user2_history) == 1

    assert user1_history[0].content == "我是用户user001"
    assert user2_history[0].content == "我是用户user002"


def test_runtime_history_reuse():
    container = ApplicationContainer()
    runtime = container.create_runtime()
    handler1 = runtime.path_handler_registry.get_handler(PathType.LLM)

    handler2 = runtime.path_handler_registry.get_handler(PathType.LLM)

    assert isinstance(handler1, LLMPathHandler)
    assert isinstance(handler2, LLMPathHandler)

    assert handler1 is handler2

    history1 = handler1.conversation_history
    history2 = handler2.conversation_history
    assert history1 is history2


class MemoryFailingLLMClient(BaseLLMClient):

    def chat(self, messages: list[LLMMessage]) -> LLMResult:
        return LLMResult(
            model="failing-mock",
            success=False,
            data=None,
            tool_calls=[],
            usage=None,
            error="模拟LLM调用失败"
        )


def test_history_saved_only_on_success():
    # 1. 创建共享的历史记录
    history = ConversationHistory()

    # 2. 使用正常的MockLLM
    handler = LLMPathHandler(
        llm_client=MockLLMClient(),
        prompt_builder=PromptBuilder(),
        conversation_history=history,
        tool_registry=ToolRegistry()
    )
    user_id = "memory_test_user"

    # 3. 第一次请求成功
    response1 = handler.handle(
        message="你好",
        user_id=user_id,
        intent="chat",

    )
    assert response1.status == "success"
    assert len(history.get_history(user_id)) == 2

    # 4.第二次请求成功
    response2 = handler.handle(
        message="我正在学习python",
        user_id=user_id,
        intent="chat"
    )
    assert response2.status == "success"
    assert len(history.get_history(user_id)) == 4

    # 5. 模拟下一次LLM调用失败
    handler.llm_client = MemoryFailingLLMClient()

    response3 = handler.handle(
        message="第三次请求",
        user_id=user_id,
        intent="chat"
    )
    # 6. 验证失败后历史没有增加
    assert response3.status == "failed"
    assert len(history.get_history(user_id)) == 4
def test_history_max_messages():
    # 1. 创建 History，最多保存 3 条消息
    history = ConversationHistory(max_messages=3)

    user_id = "user001"

    # 2. 连续添加 5 条消息
    for i in range(1, 6):
        history.add_message(
            user_id=user_id,
            message=LLMMessage(
                role=MessageRole.USER,
                content=f"消息{i}"
            )
        )

    # 3. 获取最终历史记录
    messages = history.get_history(user_id)

    # 4. 验证只保留 3 条
    assert len(messages) == 3

    # 5. 验证保留的是最新 3 条
    assert [msg.content for msg in messages] == [
        "消息3",
        "消息4",
        "消息5"
    ]
def test_get_history_returns_copy():
    # 1. 创建 History
    history = ConversationHistory()

    user_id = "user001"

    # 2. 添加一条消息
    history.add_message(
        user_id=user_id,
        message=LLMMessage(
            role=MessageRole.USER,
            content="你好"
        )
    )

    # 3. 获取历史消息
    messages = history.get_history(user_id)

    # 4. 清空返回的列表
    messages.clear()

    # 5. 再次获取内部保存的历史
    saved_messages = history.get_history(user_id)

    # 6. 验证内部历史未受到影响
    assert len(saved_messages) == 1
    assert saved_messages[0].content == "你好"

    # 7. 验证返回的列表不是内部列表本身
    assert messages is not history.messages[user_id]