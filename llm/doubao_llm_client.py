import os
from openai import OpenAI

from llm.base_llm_client import BaseLLMClient
from schemas import LLMMessage, LLMResult


class DoubaoLLMClient(BaseLLMClient):
    def __init__(self) -> None:
        api_key = os.getenv("ARK_API_KEY")
        base_url = os.getenv("ARK_BASE_URL")
        model = os.getenv("ARK_MODEL")

        if not api_key:
            raise ValueError("环境变量 ARK_API_KEY 未配置")
        if not base_url:
            raise ValueError("环境变量 ARK_BASE_URL 未配置")
        if not model:
            raise ValueError("环境变量 ARK_MODEL 未配置")
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model

    def chat(self, messages: list[LLMMessage]) -> LLMResult:
        try:
            request_messages = [
                {
                    "role": message.role.value,
                    "content": message.content
                }
                for message in messages
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=request_messages
            )

            assistant_content = (
                    response.choices[0].message.content or ""
            )
            usage = None
            if response.usage is not None:
                usage = {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            return LLMResult(
                model=self.model,
                success=True,
                data={
                    "content":assistant_content
                },
                usage=usage,
                error=None
            )
        except Exception as exc:
            return LLMResult(
                model=self.model,
                success=False,
                data=None,
                usage=None,
                error=str(exc)
            )

