from conversation.history import ConversationHistory
from schemas import LLMMessage, MessageRole


def test_history_limit() -> None:
    history = ConversationHistory(max_messages=4)

    for index in range(1, 7):
        history.add_message(
            user_id="001",
            message=LLMMessage(
                role=MessageRole.USER,
                content=f"消息{index}",
            ),
        )

    messages = history.get_history("001")

    print("历史数量：", len(messages))

    for message in messages:
        print(message.content)

    assert len(messages) == 4
    assert messages[0].content == "消息3"
    assert messages[-1].content == "消息6"


def test_defensive_copy() -> None:
    history = ConversationHistory(max_messages=4)

    history.add_message(
        user_id="001",
        message=LLMMessage(
            role=MessageRole.USER,
            content="原始消息",
        ),
    )

    external_messages = history.get_history("001")
    external_messages.clear()

    internal_messages = history.get_history("001")

    print("外部列表数量：", len(external_messages))
    print("内部历史数量：", len(internal_messages))

    assert len(external_messages) == 0
    assert len(internal_messages) == 1
    assert internal_messages[0].content == "原始消息"


def test_user_isolation() -> None:
    history = ConversationHistory(max_messages=4)

    history.add_message(
        user_id="001",
        message=LLMMessage(
            role=MessageRole.USER,
            content="用户001的消息",
        ),
    )

    history.add_message(
        user_id="002",
        message=LLMMessage(
            role=MessageRole.USER,
            content="用户002的消息",
        ),
    )

    user_001_messages = history.get_history("001")
    user_002_messages = history.get_history("002")

    assert len(user_001_messages) == 1
    assert len(user_002_messages) == 1
    assert user_001_messages[0].content == "用户001的消息"
    assert user_002_messages[0].content == "用户002的消息"


def main() -> None:
    test_history_limit()
    test_defensive_copy()
    test_user_isolation()

    print("ConversationHistory 全部测试通过")


if __name__ == "__main__":
    main()