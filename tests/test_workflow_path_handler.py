from handlers.workflow_path_handler import WorkflowPathHandler
from tool_registry import ToolRegistry
from workflow.engine import WorkflowEngine
from workflow.models import Workflow, WorkflowStep
from workflow.registry import WorkflowRegistry


def test_workflow_path_handler_success():
    tool_registry = ToolRegistry()

    workflow_engine = WorkflowEngine(
        tool_registry=tool_registry
    )

    workflow_registry = WorkflowRegistry()

    workflow = Workflow(
        name="double_calculation",
        steps=[
            WorkflowStep(
                name="calculate_first",
                tool_name="calculator",
                arguments={
                    "expression": "123*456"
                }
            ),
            WorkflowStep(
                name="calculate_second",
                tool_name="calculator",
                arguments={
                    "expression": "789+321"
                }
            )
        ]
    )

    workflow_registry.register(workflow)

    handler = WorkflowPathHandler(
        workflow_registry=workflow_registry,
        workflow_engine=workflow_engine
    )

    response = handler.handle(
        message="执行双计算工作流",
        user_id="workflow_test_001",
        intent="double_calculation"
    )

    assert response.status == "success"
    assert response.execution_path == "workflow"
    assert response.intent == "double_calculation"
def test_workflow_not_found():
    tool_registry = ToolRegistry()

    workflow_engine = WorkflowEngine(
        tool_registry=tool_registry
    )

    workflow_registry = WorkflowRegistry()

    handler = WorkflowPathHandler(
        workflow_registry=workflow_registry,
        workflow_engine=workflow_engine
    )

    response = handler.handle(
        message="执行不存在的工作流",
        user_id="workflow_test_002",
        intent="nonexistent_workflow"
    )

    assert response.status == "failed"
    assert response.execution_path == "workflow"
    assert response.intent == "nonexistent_workflow"
    assert response.result is None
    assert "nonexistent_workflow" in response.error
def test_workflow_invalid_inputs():
    tool_registry = ToolRegistry()

    workflow_engine = WorkflowEngine(
        tool_registry=tool_registry
    )

    workflow_registry = WorkflowRegistry()

    workflow = Workflow(
        name="test_invalid_inputs",
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

    workflow_registry.register(workflow)

    handler = WorkflowPathHandler(
        workflow_registry=workflow_registry,
        workflow_engine=workflow_engine
    )

    response = handler.handle(
        message="执行工作流",
        user_id="workflow_test_003",
        intent="test_invalid_inputs",
        workflow_inputs={}
    )

    assert response.status == "failed"
    assert response.execution_path == "workflow"
    assert response.error is not None
    assert "expression1" in response.error

    assert response.result["success"] is False
    assert len(response.result["step_results"]) == 1
    assert response.result["step_results"][0]["success"] is False