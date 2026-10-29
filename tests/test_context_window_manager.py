import pytest

from conversation.context_window_manager import ContextWindowManager
from schemas import LLMMessage, MessageRole


def test_estimate_tokens():
    """测试token估算：正常文本 / None / 空字符串"""
    manager = ContextWindowManager()
    messages = [
        LLMMessage(role=MessageRole.USER, content="你好世界"),
        LLMMessage(role=MessageRole.USER, content=None),
        LLMMessage(role=MessageRole.USER, content=""),
    ]
    assert manager.estimate_tokens(messages[0]) == 2
    assert manager.estimate_tokens(messages[1]) == 1
    assert manager.estimate_tokens(messages[2]) == 1


def test_trim_history_keep_latest_messages():
    """截断历史，在token上限内保留靠后的消息，顺序不变"""
    manager = ContextWindowManager(max_tokens=4)
    messages = [
        LLMMessage(role=MessageRole.USER, content="消息一一"),
        LLMMessage(role=MessageRole.USER, content="消息二二"),
        LLMMessage(role=MessageRole.USER, content="消息三三"),
        LLMMessage(role=MessageRole.USER, content="消息四四"),
    ]
    result = manager.trim_history(messages)

    assert len(result) == 2
    assert result[0].content == "消息三三"
    assert result[1].content == "消息四四"


def test_trim_history_latest_single_message_over_limit():
    """最后一条消息本身token就超限，直接返回空列表"""
    manager = ContextWindowManager(max_tokens=3)
    messages = [
        LLMMessage(role=MessageRole.USER, content="你好"),
        LLMMessage(role=MessageRole.ASSISTANT, content="abcdefghij")
    ]
    result = manager.trim_history(messages)

    assert result == []
def test_trim_history_empty():

    manager = ContextWindowManager(max_tokens=1000)

    history_messages = []

    result = manager.trim_history(history_messages)

    # 请自己补充一个 assert
    assert result ==[]
def test_trim_history_exact_budget():
    manager = ContextWindowManager(max_tokens=4)

    messages = [
        LLMMessage(
            role=MessageRole.USER,
            content="你好世界"
        ),
        LLMMessage(
            role=MessageRole.ASSISTANT,
            content="好的收到"
        )
    ]

    result = manager.trim_history(messages)

    # 请自己补充断言
    assert len(result)==2
    assert result[0].content=="你好世界"
    assert result[1].content=="好的收到"
def test_invalid_max_tokens():

    # 验证 max_tokens = 0
    with pytest.raises(ValueError):
        ContextWindowManager(max_tokens=0)

    # 验证 max_tokens = -5
    # 这里由你自己补全
    with pytest.raises(ValueError):
        ContextWindowManager(max_tokens=-5)
def test_calculate_history_budget():
    manager = ContextWindowManager()

    result1 = manager.calculate_history_budget(
        model_context_limit=10000,
        system_tokens=500,
        user_tokens=1500,
        reserved_tokens=2000
    )

    result2 = manager.calculate_history_budget(
        model_context_limit=1000,
        system_tokens=200,
        user_tokens=700,
        reserved_tokens=300
    )

    # 自己编写两个 assert
    assert result1==6000
    assert result2==0
def test_calculate_history_budget_invalid():
    manager = ContextWindowManager()

    with pytest.raises(ValueError):
        manager.calculate_history_budget(
            model_context_limit=0,
            system_tokens=100,
            user_tokens=100,
            reserved_tokens=100
        )

    # 自己补充 system_tokens 为负数的测试
    with pytest.raises(ValueError):
        manager.calculate_history_budget(
            model_context_limit=0,
            system_tokens=-100,
            user_tokens=100,
            reserved_tokens=100
        )
def test_trim_history_dynamic_budget():
    manager = ContextWindowManager(max_tokens=1000)

    messages = [
        LLMMessage(role=MessageRole.USER, content="你好世界"),
        LLMMessage(role=MessageRole.USER, content="今天很好"),
        LLMMessage(role=MessageRole.USER, content="明天见面")
    ]

    result = manager.trim_history(messages, max_tokens=4)

    # 请你自己补充断言
    assert len(result) == 2
    assert result[0].content == "今天很好"
    assert result[1].content == "明天见面"
def test_dynamic_budget_with_trim():
    manager = ContextWindowManager(max_tokens=1000)

    messages = [
        LLMMessage(role=MessageRole.USER, content="消息一一"),
        LLMMessage(role=MessageRole.USER, content="消息二二"),
        LLMMessage(role=MessageRole.USER, content="消息三三"),
        LLMMessage(role=MessageRole.USER, content="消息四四")
    ]

    history_budget = manager.calculate_history_budget(
        model_context_limit=10,
        system_tokens=2,
        user_tokens=2,
        reserved_tokens=2
    )

    trimmed = manager.trim_history(
        messages,
        max_tokens=history_budget
    )

    # 下面由你自己补充断言
    assert history_budget==4
    assert len(trimmed)==2
    assert trimmed[0].content=="消息三三"
    assert trimmed[1].content=="消息四四"
def test_trim_history_negative_budget():
    manager = ContextWindowManager()

    with pytest.raises(ValueError):
        manager.trim_history([], max_tokens=-1)
def test_calculate_history_budget_zero_user_tokens():
    manager = ContextWindowManager()

    result = manager.calculate_history_budget(
        model_context_limit=1000,
        system_tokens=100,
        user_tokens=0,
        reserved_tokens=200
    )

    assert result == 700