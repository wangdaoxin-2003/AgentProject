

import pytest


from tool_registry import ToolRegistry
from workflow.engine import WorkflowEngine
from workflow.models import Workflow, WorkflowStep,WorkflowContext


@pytest.fixture
def engine():
    tool_registry = ToolRegistry()

    return WorkflowEngine(
        tool_registry=tool_registry
    )

def test_workflow_success(engine):
    workflow = Workflow(
        name="test_success_workflow",
        steps=[
            WorkflowStep(
                name="calculate_first",
                tool_name="calculator",
                arguments={
                    "expression":"100+200"
                }
            ),
            WorkflowStep(
                name="calculate_second",
                tool_name="calculator",
                arguments={
                    "expression":"300+400"
                }
            )
        ]
    )
    context=WorkflowContext(inputs={})
    result = engine.execute(workflow,context)

    assert result.success is True
    assert result.workflow_name == "test_success_workflow"
    assert len(result.step_results) == 2
    assert result.step_results[0].data["result"] == 300
    assert result.step_results[1].data["result"] == 700

def test_workflow_step_failure_stops_execution(engine):
    workflow = Workflow(
        name="test_failure_workflow",
        steps=[
            WorkflowStep(
                name="calculate_first",
                tool_name="calculator",
                arguments={
                    "expression": "100+200"
                }
            ),
            WorkflowStep(
                name="calculate_invalid",
                tool_name="calculator",
                arguments={
                    "expression": "10/0"
                }
            ),
            WorkflowStep(
                name="calculate_third",
                tool_name="calculator",
                arguments={
                    "expression": "500+500"
                }
            )
        ]
    )
    context = WorkflowContext(inputs={})
    result = engine.execute(workflow,context)

    assert result.success is False
    assert len(result.step_results) == 2
    assert result.step_results[0].success is True
    assert result.step_results[1].success is False
    assert result.step_results[1].error == "除数不能为0"

def test_workflow_tool_not_found(engine):
    workflow = Workflow(
        name="test_tool_not_found_workflow",
        steps=[
            WorkflowStep(
                name="unknown_step",
                tool_name="nonexistent_tool",
                arguments={}
            )
        ]
    )
    context = WorkflowContext(inputs={})
    result = engine.execute(workflow,context)

    assert result.success is False
    assert len(result.step_results) == 1
    assert result.step_results[0].success is False
    assert result.step_results[0].error == "工具不存在：nonexistent_tool"
def test_workflow_step_output_reference(engine):
    workflow = Workflow(
        name="test_step_reference",
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
        inputs={"expression1": "100+200"}
    )

    result = engine.execute(workflow, context)

    assert result.success is True
    assert len(result.step_results) == 2
    assert result.step_results[0].data["result"] == 300
    assert result.step_results[1].data["result"] == 1500
    assert context.step_outputs["calculate_first"]["result"] == 300
    assert context.step_outputs["calculate_second"]["result"] == 1500

def test_workflow_missing_step_output(engine):
    workflow = Workflow(
        name="test_missing_step_output",
        steps=[
            WorkflowStep(
                name="calculate_first",
                tool_name="calculator",
                arguments={
                    "expression": "100+200"
                }
            ),
               WorkflowStep(
                name="calculate_second",
                tool_name="calculator",
                arguments={
                    "expression": "{{steps.unknown_step.result}}*5"
                }
            ),
            WorkflowStep(
                name="calculate_third",
                tool_name="calculator",
                arguments={
                    "expression": "10+20"
                }
            )
        ]
    )

    context = WorkflowContext(inputs={})

    result = engine.execute(workflow, context)

    assert result.success is False
    assert len(result.step_results) == 2

    assert result.step_results[0].success is True
    assert result.step_results[1].success is False

    assert "unknown_step" in result.step_results[1].error
    assert context.step_outputs["calculate_first"]["result"] == 300
    assert "calculate_third" not in context.step_outputs
def test_workflow_context_isolation(engine):
    workflow = Workflow(
        name="test_context_isolation",
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

    context_a = WorkflowContext(
        inputs={"expression1": "100+200"}
    )

    context_b = WorkflowContext(
        inputs={"expression1": "50+50"}
    )

    result_a = engine.execute(workflow, context_a)
    result_b = engine.execute(workflow, context_b)

    assert result_a.success is True
    assert result_b.success is True

    assert result_a.step_results[1].data["result"] == 1500
    assert result_b.step_results[1].data["result"] == 500

    assert context_a.step_outputs["calculate_first"]["result"] == 300
    assert context_b.step_outputs["calculate_first"]["result"] == 100

    assert context_a.step_outputs is not context_b.step_outputs