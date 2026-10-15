from unittest import result

from llm.doubao_llm_client import DoubaoLLMClient
from schemas import  LLMMessage, MessageRole


def main()->None:
    client = DoubaoLLMClient()
    messages=[
        LLMMessage(
            role=MessageRole.SYSTEM,
            content="你是一个专业的AI助手。"
        ),
        LLMMessage(
            role=MessageRole.USER,
            content="请用一句话介绍你自己"
        )
    ]
    result = client.chat(messages)
    print("调用是否成功：",result.success)
    print("模型：",result.model)
    print("回复数据：",result.data)
    print("Token使用：",result.usage)
    print("错误信息：",result.error)
if __name__ == "__main__":
    main()