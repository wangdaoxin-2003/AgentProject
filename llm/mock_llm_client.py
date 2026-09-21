from llm.base_llm_client import BaseLLMClient
from schemas import LLMResult, LLMMessage, ToolCall, MessageRole


class MockLLMClient(BaseLLMClient):
    def chat(self, messages: list[LLMMessage]) -> LLMResult:
        if not messages:
            return LLMResult(
                model="mock-llm",
                success=False,
                data=None,
                usage=None,
                error="messages 不能为空"
            )
        latest_user_message = self._get_latest_user_message(messages)
        if latest_user_message is None:
            return LLMResult(
                model="mock-llm",
                success=False,
                data=None,
                usage=None,
                error="没有找到用户消息"
            )
        latest_user_content = latest_user_message.content
        if latest_user_content.startswith("计算"):
            expression = latest_user_content.removeprefix("计算").strip()
            return LLMResult(
                model="mock-llm",
                success=True,
                data={
                    "content": "",
                },
                tool_calls=[
                    ToolCall(
                        id="call_001",
                        name="calculator",
                        arguments={
                            "expression": expression
                        }
                    )
                ],
                usage=None,
                error=None
            )
        return LLMResult(
            model="mock-llm",
            success=True,
            data={
                "content": f"这是 Mock LLM收到消息：{latest_user_content}",
            },
            tool_calls=None,
            usage=None,
            error=None
        )

    def _get_latest_user_message(self, messages: list[LLMMessage]) -> LLMMessage:
        for message in reversed(messages):
            if message.role == MessageRole.USER:
                return message
        return None
