from typing import Any

import workflow
from schemas import AgentResponse
from workflow.engine import WorkflowResult, WorkflowEngine
from workflow.models import WorkflowContext
from workflow.registry import WorkflowRegistry
from handlers.base_path_handler import BasePathHandler


class WorkflowPathHandler(BasePathHandler):
    def __init__(
            self,
            workflow_registry: WorkflowRegistry,
            workflow_engine: WorkflowEngine
    ):
        self.workflow_registry = workflow_registry
        self.workflow_engine = workflow_engine

    def handle(self, message: str, user_id: str, intent: str,
               workflow_inputs: dict[str, Any] | None = None) -> AgentResponse:
        workflow = self.workflow_registry.get_workflow(intent)
        if workflow is None:
            return AgentResponse(
                message="未找到对应工作流",
                user_id=user_id,
                intent=intent,
                execution_path="workflow",
                status="failed",
                result=None,
                error=f"工作流不存在{intent}"
            )
        context = WorkflowContext(
            inputs=workflow_inputs if workflow_inputs is not None else {}
        )

        workflow_result = self.workflow_engine.execute(workflow,context)
        if workflow_result.success:
            return AgentResponse(
                message="Workflow执行成功",
                user_id=user_id,
                intent=intent,
                execution_path="workflow",
                status="success",
                result=workflow_result.model_dump(),
                error=None
            )
        return AgentResponse(
            message="Workflow执行失败",
            user_id=user_id,
            intent=intent,
            execution_path="workflow",
            status="failed",
            result=workflow_result.model_dump(),
            error=workflow_result.error
        )
