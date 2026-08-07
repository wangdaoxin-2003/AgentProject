from schemas import LLMMessage


class ConversationHistory:
    def __init__(self, max_messages: int = 20):

        if max_messages <= 0:
            raise ValueError("max_messages 必须大于0")
        self.max_messages = max_messages
        self.messages: dict[str, list[LLMMessage]] = {}

    def add_message(self, user_id: str, message: LLMMessage) -> None:
        if user_id not in self.messages:
            self.messages[user_id] = []
        self.messages[user_id].append(message)

        if len(self.messages[user_id]) > self.max_messages:
            self.messages[user_id] = self.messages[user_id][-self.max_messages:]

    def get_history(self, user_id: str) -> list[LLMMessage]:
        return self.messages.get(user_id, []).copy()
