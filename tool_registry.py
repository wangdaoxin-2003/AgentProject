from tools.base_tool import BaseTool
from tools.chat_tool import ChatTool
from tools.weather_tool import WeatherTool
from tools.calculator_tool import CalculatorTool

class ToolRegistry:#定义工具注册中心（一个保存所有工具的工具箱）

    def __init__(self):#创建工具字典
        tool_list: list[BaseTool] = [
            WeatherTool(),
            CalculatorTool(),
            ChatTool(),
        ]
        self.tools = {tool.name: tool for tool in tool_list}
    def get_tool(self, intent: str):
        return self.tools.get(intent)