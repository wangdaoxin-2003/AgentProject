from schemas import AgentResponse,WorkflowStepResult,WorkflowResult
from handlers.base_path_handler import BasePathHandler


class WorkflowPathHandler(BasePathHandler):
    def __init__(self):
        pass
    def handle(self, message: str, user_id: str, intent: str) -> AgentResponse:
        try :
            workflow_result = WorkflowResult(
                workflow_name="mock_workflow",
                steps=[
                    WorkflowStepResult(
                        step=1,
                        name="接收用户请求",
                        status="success",
                        data={
                            "message": message
                        },
                        error=None
                    ),
                    WorkflowStepResult(
                        step=2,
                        name="模拟执行工作流",
                        status="success",
                        data={
                            "message": "模拟工作流执行成功"
                        },
                        error=None
                    ),
                    WorkflowStepResult(
                        step=3,
                        name="返回结果给用户",
                        status="success",
                        data=None,
                        error=None
                    )
                ],
                original_message=message
            )
            return AgentResponse(
                message="Workflow执行成功",
                user_id=user_id,
                intent=intent,
                execution_path="workflow",
                status="success",
                result=workflow_result.model_dump(),
                error=None
            )
        except Exception as e:
            return AgentResponse(
                message="Workflow执行失败",
                user_id=user_id,
                intent=intent,
                execution_path="workflow",
                status="failed",
                result=None,
                error=str(e)
            )
