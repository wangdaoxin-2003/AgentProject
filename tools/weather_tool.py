from tools.base_tool import BaseTool
from schemas import ToolResult

class WeatherTool(BaseTool):  # 天气查询工具
    name = "weather"

    def execute(self, message: str) -> ToolResult:  # 执行方法
        return ToolResult(
            tool=self.name,
            success=True,
            data={
                "result":"天气工具执行成功"
            },
            error= None
        )
