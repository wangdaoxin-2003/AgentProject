from pydantic import BaseModel,Field
from typing import Any

class WorkflowStep(BaseModel):
    name:str
    tool_name:str
    arguments:dict[str,Any]
class Workflow(BaseModel):
    name:str
    steps:list[WorkflowStep]

class WorkflowStepResult(BaseModel):
    step_name:str
    success:bool
    data:dict[str,Any] | None = None
    error :str | None = None

class WorkflowResult(BaseModel):
    workflow_name:str
    success:bool
    step_results:list[WorkflowStepResult]
    error:str | None = None

class WorkflowContext(BaseModel):
    inputs: dict[str,Any]
    step_outputs: dict [str,Any] = Field(default_factory=dict)