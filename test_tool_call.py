from schemas import LLMResult, ToolCall

tool_call = ToolCall(
    id="call_001",
    name="calculator",
    arguments={
        "expression": "100+200"
    }
)

llm_result = LLMResult(
    model="mock-llm",
    success=True,
    data={
        "content": ""
    },
    tool_calls=[
        tool_call
    ],
    usage=None,
    error=None
)

print("模型：", llm_result.model)
print("是否成功：", llm_result.success)
print("工具调用数量：", len(llm_result.tool_calls))

first_tool_call = llm_result.tool_calls[0]

print("工具名称：", first_tool_call.name)
print("工具参数：", first_tool_call.arguments)
