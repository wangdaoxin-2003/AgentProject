from workflow.models import Workflow


class WorkflowRegistry:
    def __init__(self):
        self.workflows:dict[str,Workflow] = {}

    def register(self,workflow:Workflow) -> None:
        self.workflows[workflow.name] = workflow
    def get_workflow(self,name:str) -> Workflow | None:
        return self.workflows.get(name)

