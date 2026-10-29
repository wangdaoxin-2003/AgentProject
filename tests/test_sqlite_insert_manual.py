from conversation.sqlite_history import SQLiteConversationHistory
from schemas import LLMMessage, MessageRole
import sqlite3

def test_sqlite_insert(tmp_path):
    # 使用 pytest 提供的临时目录
    db_path = tmp_path / "agent_memory.db"

    history = SQLiteConversationHistory(db_path)
    history.create_table()

    message = LLMMessage(
        role=MessageRole.USER,
        content="你好，我叫小明"
    )

    history.add_message("user_001", message)

    # 下一步验证数据库内容
    conn = sqlite3.connect(db_path)

    try:
        row = conn.execute(
            """
            SELECT user_id, role, content
            FROM messages
            WHERE user_id = ?
            """,
            ("user_001",)
        ).fetchone()
    finally:
        conn.close()
    assert row is not None
    assert row[0]=="user_001"
    assert row[1]=="user"
    assert row[2]=="你好，我叫小明"
def test_sqlite_get_history(tmp_path):
    db_path = tmp_path / "agent_memory.db"

    history = SQLiteConversationHistory(db_path)
    history.create_table()

    history.add_message(
        "user_A",
        LLMMessage(role=MessageRole.USER, content="我是A")
    )

    history.add_message(
        "user_B",
        LLMMessage(role=MessageRole.USER, content="我是B")
    )

    history.add_message(
        "user_A",
        LLMMessage(
            role=MessageRole.ASSISTANT,
            content="你好A"
        )
    )

    messages = history.get_history("user_A")

    # 下面由你自己补充 assert
    assert len(messages)==2
    assert messages[0].content=="我是A"
    assert messages[1].content=="你好A"
def test_sqlite_max_messages(tmp_path):
    db_path = tmp_path / "memory.db"

    history = SQLiteConversationHistory(
        db_path=db_path,
        max_messages=3
    )
    history.create_table()

    for i in range(5):
        history.add_message(
            "user_A",
            LLMMessage(
                role=MessageRole.USER,
                content=f"消息{i + 1}"
            )
        )

    messages = history.get_history("user_A")

    assert len(messages)==3
    assert messages[0].content=="消息3"
    assert messages[-1].content=="消息5"