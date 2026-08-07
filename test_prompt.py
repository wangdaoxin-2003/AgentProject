from prompt.prompt_builder import PromptBuilder
from conversation.history import ConversationHistory
from schemas import MessageRole, LLMMessage

history=ConversationHistory()
history.add_message("001",LLMMessage(
    role=MessageRole.USER,
    content="今天天气如何？"
))
history.add_message("001",LLMMessage(
    role=MessageRole.ASSISTANT,
    content="今天天气不错，多云。"
))
builder = PromptBuilder()
messages = builder.build("帮我分析一下这个广告", history_messages= history.get_history("001"))

for msg in messages:
    print(msg.content)