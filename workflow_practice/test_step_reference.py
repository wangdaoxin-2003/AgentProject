from workflow_practice.models import (
    Workflow,
    WorkflowStep,
    WorkflowContext
)
from tool_registry import ToolRegistry
from workflow_practice.engine import WorkflowEngine

workflow = Workflow(
    name="practice_double_calculation",
    steps=[
        WorkflowStep(
            name="calculate_first",
            tool_name="calculator",
            arguments={
                "expression": "{{expression1}}"
            }
        ),
        WorkflowStep(
            name="calculate_second",
            tool_name="calculator",
            arguments={
                "expression": "{{steps.calculate_first.result}}*5"
            }
        )
    ]
)
context = WorkflowContext(
    inputs={
        "expression1": "100+200"
    }
)

tool_registry = ToolRegistry()

engine = WorkflowEngine(tool_registry)
result = engine.execute(workflow, context)

print(result.model_dump())
print(context.step_outputs)

assert result.success is True
assert len(result.step_results) == 2

assert result.step_results[0].data["result"] == 300
assert result.step_results[1].data["result"] == 1500

assert context.step_outputs["calculate_first"]["result"] == 300
assert context.step_outputs["calculate_second"]["result"] == 1500

print("Step1 → Step2 数据传递验证成功")