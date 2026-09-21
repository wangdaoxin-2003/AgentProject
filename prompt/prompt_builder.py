
from schemas import LLMMessage,MessageRole


class PromptBuilder:
    def build(self,user_message:str,history_messages:list[LLMMessage])->list[LLMMessage]:
        messages=[
            LLMMessage(role=MessageRole.SYSTEM,content="你是一个专业的AI助手。")
        ]
        messages.extend(history_messages)
        messages.append(LLMMessage(role=MessageRole.USER,content=user_message))
        return messages