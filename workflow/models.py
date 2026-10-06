from pydantic import BaseModel
from typing import Any

class WorkflowStep(BaseModel):
    name:str
    tool_name:str
    arguments:dict[str,Any]
class Workflow(BaseModel):
    name:str
    steps:list[WorkflowStep]