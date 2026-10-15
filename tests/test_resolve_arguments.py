from workflow.engine import WorkflowEngine
from workflow.models import Workflow, WorkflowStep, WorkflowContext
from tool_registry import ToolRegistry

engine = WorkflowEngine(ToolRegistry())

workflow = Workflow(
    name="dynamic_calculation",
    steps=[
        WorkflowStep(
            name="calculate_first",
            tool_name="calculator",
            arguments={
                "expression": "{{expression1}}"
            }
        )
    ]
)

context = WorkflowContext(
    inputs={
        "expression1": "10+20"
    }
)

result = engine.execute(workflow, context)

assert result.success is True
assert result.step_results[0].data["result"] == 30

print(result.model_dump())