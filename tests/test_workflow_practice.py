from workflow_practice.models import (
    Workflow,
    WorkflowStep,
    WorkflowContext
)
from workflow_practice.engine import WorkflowEngine
from tool_registry import ToolRegistry
from tools.calculator_tool import CalculatorTool
def test_practice_step_output_reference():
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
        inputs={"expression1": "100+200"}
    )

    tool_registry = ToolRegistry()
    engine = WorkflowEngine(tool_registry)
    result = engine.execute(workflow, context)

    assert result.success is True
    assert len(result.step_results) == 2

    assert result.step_results[0].data["result"] == 300
    assert result.step_results[1].data["result"] == 1500

    assert context.step_outputs["calculate_first"]["result"] == 300

def test_practice_tool_not_found():
    workflow = Workflow(
        name="test_missing_tool",
        steps=[
            WorkflowStep(
                name="calculate_first",
                tool_name="unknown_tool",
                arguments={"expression": "100+200"}
            ),
            WorkflowStep(
                name="calculate_second",
                tool_name="calculator",
                arguments={"expression": "50+50"}
            )
        ]
    )
    context = WorkflowContext(inputs={})

    tool_registry = ToolRegistry()

    engine = WorkflowEngine(tool_registry)
    result = engine.execute(workflow, context)
    assert result.success is False

    assert len(result.step_results) == 1

    assert result.step_results[0].step_name == "calculate_first"

    assert result.step_results[0].success is False

    assert "unknown_tool" in result.step_results[0].error
def test_practice_tool_execution_failure():
    workflow = Workflow(
        name="test_tool_execution_failure",
        steps=[
            WorkflowStep(
                name="calculate_first",
                tool_name="calculator",
                arguments={"expression": "100+200"}
            ),
            WorkflowStep(
                name="calculate_second",
                tool_name="calculator",
                arguments={"expression": "10/0"}
            ),
            WorkflowStep(
                name="calculate_third",
                tool_name="calculator",
                arguments={"expression": "50+50"}
            )
        ]
    )
    context = WorkflowContext(inputs={})

    tool_registry = ToolRegistry()
    engine = WorkflowEngine(tool_registry)
    result = engine.execute(workflow, context)

    assert result.success is False
    assert len(result.step_results) == 2

    assert result.step_results[0].step_name == "calculate_first"
    assert result.step_results[0].success is True
    assert result.step_results[0].data["result"] == 300

    assert result.step_results[1].step_name == "calculate_second"
    assert result.step_results[1].success is False
    assert result.step_results[1].error is not None

    assert "calculate_third" not in context.step_outputs
    assert context.step_outputs["calculate_first"]["result"] == 300
    assert "calculate_second" not in context.step_outputs

def test_practice_missing_input():
    workflow = Workflow(
        name="test_missing_input",
        steps=[
            WorkflowStep(
                name="calculate_first",
                tool_name="calculator",
                arguments={"expression": "100+200"}
            ),
            WorkflowStep(
                name="calculate_second",
                tool_name="calculator",
                arguments={"expression": "{{expression2}}"}
            ),
            WorkflowStep(
                name="calculate_third",
                tool_name="calculator",
                arguments={"expression": "50+50"}
            )
        ]
    )
    context = WorkflowContext(inputs={})

    tool_registry = ToolRegistry()
    engine = WorkflowEngine(tool_registry)
    result = engine.execute(workflow, context)
    assert result.success is False
    assert len(result.step_results) == 2

    assert result.step_results[0].success is True
    assert result.step_results[0].data["result"] == 300

    assert result.step_results[1].success is False
    assert "expression2" in result.step_results[1].error

    assert "calculate_second" in result.error

    assert context.step_outputs["calculate_first"]["result"] == 300
    assert "calculate_second" not in context.step_outputs
    assert "calculate_third" not in context.step_outputs
def test_practice_context_isolation():
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
    tool_registry = ToolRegistry()
    engine = WorkflowEngine(tool_registry)
    result_a = engine.execute(workflow, context_a)

    result_b = engine.execute(workflow, context_b)
    assert result_a.success is True
    assert result_b.success is True

    assert result_a.step_results[1].data["result"] == 1500
    assert result_b.step_results[1].data["result"] == 500
    assert context_a.step_outputs["calculate_first"]["result"] == 300
    assert context_b.step_outputs["calculate_first"]["result"] == 100
    assert context_a.step_outputs is not context_b.step_outputs