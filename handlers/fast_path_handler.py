from schemas import AgentResponse
from tool_registry import ToolRegistry
from handlers.base_path_handler import BasePathHandler


class FastPathHandler(BasePathHandler):
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry

    def handle(self, message: str, user_id: str, intent: str) -> AgentResponse:
        tool = self.tool_registry.get_tool(intent)
        if tool is None:
            return AgentResponse(
                message="未找到可以处理该请求的工具",
                user_id=user_id,
                intent=intent,
                execution_path="fast",
                status="failed",
                result=None,
                error="未找到对应的工具"
            )
        try:
            tool_result = tool.execute(message)
            if tool_result.success is True:
                return AgentResponse(
                    message="工具执行成功",
                    user_id=user_id,
                    intent=intent,
                    execution_path="fast",
                    status="success",
                    result=tool_result.data,
                    error=None
                )
            return AgentResponse(
                message="工具执行失败",
                user_id=user_id,
                intent=intent,
                execution_path="fast",
                status="failed",
                result=tool_result.data,
                error=tool_result.error
            )
        except Exception as e:
            return AgentResponse(
                message="工具执行异常",
                user_id=user_id,
                intent=intent,
                execution_path="fast",
                status="failed",
                result=None,
                error=str(e)
            )
