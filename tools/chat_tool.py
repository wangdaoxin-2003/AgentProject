from tools.base_tool import BaseTool
from schemas import ToolResult

class ChatTool(BaseTool):  # 聊天工具
    name = "chat"

    def execute(self, message: str) -> ToolResult:
        return ToolResult (
            tool=self.name,
            success=True,
            data={
                "content": f"占位回复：{message}"
            },
            error= None
        )