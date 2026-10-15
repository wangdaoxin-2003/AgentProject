from fastapi import FastAPI

from container import ApplicationContainer
from schemas import AgentRequest, AgentResponse
from logging_config import setup_logging


setup_logging()
app = FastAPI(title="Amazon Agent")

container = ApplicationContainer()
runtime = container.create_runtime()  # 标识根据AgentRuntime这个类创建一个真正可以使用的对象


@app.get("/")
def health_check():
    return {"message": "Agent Project is running"}


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest):
    result = runtime.run(
        message=request.message,
        user_id=request.user_id,
        workflow_inputs=request.workflow_inputs
    )
    return result
