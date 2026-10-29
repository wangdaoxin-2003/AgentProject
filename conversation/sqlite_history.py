import sqlite3
from pathlib import Path

from conversation.base_history import BaseConversationHistory
from schemas import LLMMessage, MessageRole


class SQLiteConversationHistory(BaseConversationHistory):
    def __init__(self,db_path="data/agent_memory.db",max_messages:int =20):
        self.db_path= Path(db_path)
        if max_messages <= 0:
            raise ValueError("max_messages 必须大于0")

        self.max_messages = max_messages

    def create_table(self):
        # 1. 确保数据库所在目录存在
        # 2. 连接 SQLite 数据库
        # 3. 执行 CREATE TABLE SQL
        # 4. 提交事务
        # 5. 关闭数据库连接
        self.db_path.parent.mkdir(
            parents=True, exist_ok=True
        )
        conn =sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS messages
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             TEXT
                             NOT
                             NULL,
                             role
                             TEXT
                             NOT
                             NULL,
                             content
                             TEXT
                         );
                         """)
            conn.commit()
        finally:
            conn.close()
    def add_message(self,user_id:str,message:LLMMessage):

        conn=sqlite3.connect(self.db_path)
        try:
            conn.execute("""
            INSERT INTO messages (user_id,role,content)
                values (?,?,?)
            """,(user_id,message.role.value,message.content))
            conn.commit()
        finally:
            conn.close()

    def get_history(self,user_id:str)->list[LLMMessage]:

        conn=sqlite3.connect(self.db_path)
        try:
            rows=conn.execute("""
                              SELECT role, content
                              FROM (SELECT id, role, content
                                    FROM messages
                                    WHERE user_id = ?
                                    ORDER BY id DESC LIMIT ?)
                              ORDER BY id ASC;
                              """,(user_id,self.max_messages)).fetchall()

        finally:
            conn.close()

        messages = []
        for role, content in rows:
            message = LLMMessage(
                role=MessageRole(role),
                content=content
            )
            messages.append(message)
        return messages