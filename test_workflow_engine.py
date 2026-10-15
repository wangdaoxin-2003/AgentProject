from workflow.engine import WorkflowEngine
from workflow.models import WorkflowContext
from tool_registry import ToolRegistry

engine = WorkflowEngine(ToolRegistry())

context = WorkflowContext(
    inputs={},
    step_outputs={
        "calculate_first": {
            "result": 300
        }
    }
)

arguments = {
    "previous_result": "{{steps.calculate_first.result}}",
    "multiplier": 5
}

result = engine._resolve_arguments(
    arguments,
    context
)

print(result)

assert result == {
    "previous_result": 300,
    "multiplier": 5
}

print("Step输出引用测试通过")
