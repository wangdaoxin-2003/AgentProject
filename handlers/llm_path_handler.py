from conversation.history import ConversationHistory
from llm.base_llm_client import BaseLLMClient
from schemas import AgentResponse, LLMMessage, MessageRole, LLMResult
from handlers.base_path_handler import BasePathHandler
from prompt.prompt_builder import PromptBuilder
from tool_registry import ToolRegistry


class LLMPathHandler(BasePathHandler):
    def __init__(self, llm_client: BaseLLMClient, prompt_builder: PromptBuilder,
                 conversation_history: ConversationHistory,tool_registry: ToolRegistry):
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder
        self.conversation_history = conversation_history
        self.tool_registry = tool_registry

    def handle(self, message: str, user_id: str, intent: str) -> AgentResponse:
        try:
            history_messages = self.conversation_history.get_history(user_id=user_id)
            messages = self.prompt_builder.build(user_message=message,
                                                 history_messages=history_messages)
            llm_result = self.llm_client.chat(messages)

            if llm_result.tool_calls:
                first_tool_call=llm_result.tool_calls[0]
                tool = self.tool_registry.get_tool(
                    first_tool_call.name
                )
                if tool is None:
                    return AgentResponse(
                        message="未找到对应的工具",
                        user_id=user_id,
                        intent=intent,
                        execution_path="llm",
                        status="failed",
                        result=None,
                        error="未找到对应的工具"
                    )
                tool_result = tool.execute(first_tool_call.arguments)
                messages.append(
                    LLMMessage(
                        role=MessageRole.TOOL,
                        content=str(tool_result.data),
                    )
                )
                final_result = self.llm_client.chat(messages)
                final_content=""
                if final_result.data:
                    final_content = final_result.data.get("content","")
                return AgentResponse(
                    message=final_content,
                    user_id=user_id,
                    intent=intent,
                    execution_path="llm",
                    status="success",
                    result={
                        "tool_result":tool_result.model_dump(),
                        "final_llm_result":final_result.model_dump(),
                        "tool_call":{
                            "id":first_tool_call.id,
                            "name":first_tool_call.name,
                            "arguments":first_tool_call.arguments
                        }
                    },
                    error=None
                )

            if llm_result.success is not True:
                return AgentResponse(
                    message="LLM执行失败",
                    user_id=user_id,
                    intent=intent,
                    execution_path="llm",
                    status="failed",
                    result=llm_result.model_dump(),
                    error=llm_result.error
                )
            assistant_content = ""
            if llm_result.data is not None:
                assistant_content = str(llm_result.data.get("content"))
            self.conversation_history.add_message(
                user_id=user_id,
                message=LLMMessage(
                    role=MessageRole.USER,
                    content=message
                )
            )
            self.conversation_history.add_message(
                user_id=user_id,
                message=LLMMessage(
                    role=MessageRole.ASSISTANT,
                    content=assistant_content
                )
            )
            return AgentResponse(
                message="LLM执行成功",
                user_id=user_id,
                intent=intent,
                execution_path="llm",
                status="success",
                result=llm_result.model_dump(),
                error=None
            )
        except Exception as e:
            return AgentResponse(
                message="LLM执行异常",
                user_id=user_id,
                intent=intent,
                execution_path="llm",
                status="failed",
                result=None,
                error=str(e)
            )
