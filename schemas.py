from contextlib import AbstractAsyncContextManager
from typing import Any
from pydantic import BaseModel
from enum import Enum


class AgentRequest(BaseModel):  # 负责约束客户端传进来的数据的格式
    message: str
    user_id: str


class AgentResponse(BaseModel):  # 负责约束服务器返回的数据格式
    message: str
    user_id: str
    intent: str
    execution_path: str
    status: str
    result: dict[str, Any] | None = None  # =None表示参数没有时默认值是None
    error: str | None = None


class ToolResult(BaseModel):  # 负责约束Tool的统一返回格式
    tool: str
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


class ToolCall(BaseModel):  # LLM工具调用
    id: str
    name: str
    arguments: dict[str, Any]


class LLMResult(BaseModel):  # 负责约束LLM统一返回格式
    model: str
    tool_calls: list[ToolCall] | None = None
    success: bool
    data: dict[str, Any] | None = None
    usage: dict[str, Any] | None = None
    error: str | None = None


class WorkflowStepResult(BaseModel):  # 工作流步骤结果
    step: int  # 步骤编号
    name: str  # 步骤名称
    status: str  # 步骤执行状态
    data: dict[str, Any] | None = None  # 保存该步骤产生的结果
    error: str | None = None  # 记录步骤失败的原因，成功时为None


class WorkflowResult(BaseModel):  # 整个工作流最终的执行结果
    workflow_name: str
    steps: list[WorkflowStepResult]
    original_message: str


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class LLMMessage(BaseModel):
    role: MessageRole
    content: str
