from tools.base_tool import BaseTool
from parameter_extractor import ParameterExtractor
from schemas import ToolResult
from typing import Any


class CalculatorTool(BaseTool):  # 计算工具
    name = "calculator"

    def __init__(self):
        self.parameter_extractor = ParameterExtractor()

    def execute(self, message: str | dict[str, Any]):
        if isinstance(message, str):
            params = self.parameter_extractor.extract_calculator_params(message)
        else:
            expression = message.get("expression")
            if expression is None:
                return ToolResult(
                    tool=self.name,
                    success=False,
                    data=None,
                    error="没有识别到表达式"
                )
            params = self.parameter_extractor.extract_calculator_params(expression)
        if params is None:
            return ToolResult(
                tool=self.name,
                success=False,
                data=None,
                error="没有识别到两个数字"
            )
        number1 = params["number1"]
        number2 = params["number2"]
        operator = params["operator"]
        if operator == "add":
            result = number1 + number2
        elif operator == "subtract":
            result = number1 - number2
        elif operator == "multiply":
            result = number1 * number2
        elif operator == "divide":
            if number2 == 0:
                return ToolResult(
                    tool=self.name,
                    success=False,
                    data=None,
                    error="除数不能为0"
                )
            result = number1 / number2
        else:
            return ToolResult(
                tool=self.name,
                success=False,
                data=None,
                error="不支持的运算符"
            )
        return ToolResult(
            tool=self.name,
            success=True,
            data={
                "number1": number1,
                "number2": number2,
                "operator": operator,
                "result": result
            },
            error=None
        )

    def _resolve_params(self, message: str | dict[str, Any]) -> dict[str, Any] | None:
        if isinstance(message, str):
            return self.parameter_extractor.extract_calculator_params(message)
        expression = message.get("expression")
        if not isinstance(expression, str):
            return None
        return self.parameter_extractor.extract_calculator_params(expression)
