import os
from openai import OpenAI

import json
import logging
from llm.base_llm_client import BaseLLMClient
from schemas import LLMMessage, LLMResult,ToolCall

logger = logging.getLogger(__name__)

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
            request_messages = []
            for message in messages:
                request_message={
                    "role":message.role.value,
                    "content":message.content
                }
                if message.tool_calls:
                    request_message["tool_calls"] = [
                        {
                            "id": tool_call.id,
                            "type":"function",
                            "function":{
                                "name":tool_call.name,
                                "arguments":json.dumps(
                                    tool_call.arguments,
                                    ensure_ascii=False
                                )
                            }
                        }
                        for tool_call in message.tool_calls
                    ]
                if message.tool_call_id:
                    request_message["tool_call_id"] = message.tool_call_id
                request_messages.append(request_message)
            tools = [
                {
                    "type":"function",
                    "function":{
                        "name":"calculator",
                        "description":"执行数学计算。当用户要求进行数学计算时，应使用此工具进行计算，不要自行计算结果。",
                        "parameters":{
                            "type":"object",
                            "properties":{
                                "expression": {
                                    "type": "string",
                                    "description": "需要计算的数学表达式，例如10+20"
                                }
                            },
                            "required": ["expression"]
                        }
                    }
                }
            ]
            # print(request_messages)
            logger.info("llm request started: model=%s message_count=%s",self.model,len(messages))

            response = self.client.chat.completions.create(
                model=self.model,
                messages=request_messages,
                tools=tools
            )

            response_message =response.choices[0].message
            tool_calls =[]
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    arguments = json.loads(
                        tool_call.function.arguments
                    )
                    tool_calls.append(
                        ToolCall(
                            id = tool_call.id,
                            name=tool_call.function.name,
                            arguments= arguments
                        )
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
            logger.info("llm request completed: model=%s tool_call_count=%s",self.model,len(tool_calls))

            return LLMResult(
                model=self.model,
                success=True,
                data={
                    "content":assistant_content
                },
                tool_calls=tool_calls,
                usage=usage,
                error=None
            )
        except Exception as exc:

            logger.exception("llm request failed: model=%s",self.model)
            return LLMResult(
                model=self.model,
                success=False,
                data=None,
                usage=None,
                error=str(exc)
            )

