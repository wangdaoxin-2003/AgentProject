import re

from idna import valid_label_length

from tool_registry import ToolRegistry
from workflow_practice.models import Workflow, WorkflowStepResult, WorkflowResult, WorkflowContext


class WorkflowEngine:
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry

    def _resolve_arguments(self, arguments: dict, context: WorkflowContext) -> dict:
        def get_variable(variable_name:str):
            #判断是否是第一步骤的结果
            if variable_name.startswith("steps."):
                parts = variable_name.split(".")
                if len(parts)!=3:
                    raise ValueError(
                        f"无效的步骤引用：{variable_name}"
                    )
                step_name = parts[1]
                field_name = parts[2]

                if step_name not in context.step_outputs:
                    raise ValueError(
                        f"步骤'{step_name}'没有输出"
                    )
                step_output = context.step_outputs[step_name]
                if field_name not in step_output:
                    raise ValueError(
                        f"步骤'{step_name}'不存在字段'{field_name}'"
                    )
                return step_output[field_name]
            #执行到这说明不是中间结果，接下来判断是否是开头的
            if variable_name not in context.inputs:
                raise ValueError(
                    f"变量'{variable_name}'不存在"
                )
            return context.inputs[variable_name]
        #替换函数
        def replace_variable(match):
            variable_name = match.group(1)
            variable_value = get_variable(variable_name)
            return str(variable_value)

        resolved_arguments = {}
        pattern = r"\{\{([\w+.]+)\}\}"
        for key, value in arguments.items():
            if not isinstance(value, str):
                resolved_arguments[key] = value
                continue
            match = re.fullmatch(pattern, value)
            if match:
                resolved_arguments[key]= get_variable(
                    match.group(1)
                )
                continue
            #第三种情况"{{steps.calculate_first.result}}*5"
            resolved_arguments[key] = re.sub(
                pattern,
                replace_variable,
                value
            )

        return resolved_arguments

    def execute(self, workflow: Workflow, context: WorkflowContext) -> WorkflowResult:
        results = []
        for step in workflow.steps:
            print(f"当前执行步骤：{step.name}")
            tool = self.tool_registry.get_tool(step.tool_name)
            if tool is None:
                step_result = WorkflowStepResult(
                    step_name=step.name,
                    success=False,
                    data=None,
                    error=f"工具不存在：{step.tool_name}"
                )
                results.append(step_result)
                return WorkflowResult(
                    workflow_name=workflow.name,
                    success=False,
                    step_results=results,
                    error=f"步骤执行失败：{step.name},工具不存在：{step.tool_name}"
                )

            try:
                resolved_arguments = self._resolve_arguments(step.arguments, context)
            except ValueError as e:
                step_result = WorkflowStepResult(
                    step_name=step.name,
                    success=False,
                    data=None,
                    error=str(e)
                )
                results.append(step_result)

                return WorkflowResult(
                    workflow_name=workflow.name,
                    success=False,
                    step_results=results,
                    error=f"步骤参数解析失败：{step.name}，原因：{e}"
                )

            tool_result = tool.execute(resolved_arguments)

            step_result = WorkflowStepResult(
                step_name=step.name,
                success=tool_result.success,
                data=tool_result.data,
                error=tool_result.error
            )
            results.append(step_result)

            if not step_result.success:
                return WorkflowResult(
                    workflow_name=workflow.name,
                    success=False,
                    step_results=results,
                    error=f"步骤执行失败：{step_result.step_name}"
                )
            context.step_outputs[step.name] = tool_result.data
        return WorkflowResult(
            workflow_name=workflow.name,
            success=True,
            step_results=results,
            error=None
        )
