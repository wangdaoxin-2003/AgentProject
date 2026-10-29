from conversation.base_history import BaseConversationHistory
from conversation.history import ConversationHistory
from llm.base_llm_client import BaseLLMClient
from schemas import AgentResponse, LLMMessage, MessageRole, LLMResult
from handlers.base_path_handler import BasePathHandler
from prompt.prompt_builder import PromptBuilder
import json
import logging
from tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class LLMPathHandler(BasePathHandler):
    def __init__(self, llm_client: BaseLLMClient, prompt_builder: PromptBuilder,
                 conversation_history: BaseConversationHistory,tool_registry: ToolRegistry):
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder
        self.conversation_history = conversation_history
        self.tool_registry = tool_registry

    def handle(self, message: str, user_id: str, intent: str) -> AgentResponse:
        try:
            history_messages = self.conversation_history.get_history(user_id=user_id)
            messages = self.prompt_builder.build(user_message=message,
                                                 history_messages=history_messages)
            max_iterations = 5
            iteration = 0
            while True:

                if iteration >= max_iterations:
                    logger.warning(
                        "tool loop max iterations reached: user_id=%s max_iterations=%s",
                        user_id,
                        max_iterations
                    )
                    return AgentResponse(
                        message="Tool Loop超过最大执行次数",
                        user_id=user_id,
                        intent=intent,
                        execution_path="llm",
                        status="failed",
                        result=None,
                        error=f"Tool Loop超过最大执行次数：{max_iterations}"
                    )

                iteration += 1

                logger.info("tool loop iteration started: user_id=%s iteration=%s",user_id,iteration)

                llm_result = self.llm_client.chat(messages)

                if llm_result.success is not True:
                    logger.error(
                        "llm execution failed in tool loop: user_id=%s iteration=%s error=%s",
                        user_id,
                        iteration,
                        llm_result.error
                    )
                    return AgentResponse(
                        message="LLM执行失败",
                        user_id=user_id,
                        intent=intent,
                        execution_path="llm",
                        status="failed",
                        result=None,
                        error=llm_result.error

                    )

                if not llm_result.tool_calls:
                    logger.info(
                        "tool loop completed: user_id=%s iteration=%s",
                        user_id,
                        iteration
                    )
                    break

                logger.info(
                    "tool calls requested: user_id=%s iteration=%s count=%s",
                    user_id,
                    iteration,
                    len(llm_result.tool_calls)
                )

                messages.append(
                    LLMMessage(
                        role=MessageRole.ASSISTANT,
                        content=None,
                        tool_calls=llm_result.tool_calls
                    )
                )

                for tool_call in llm_result.tool_calls:
                    tool = self.tool_registry.get_tool(tool_call.name)
                    if tool is None:

                        logger.warning(
                            "tool not found: user_id=%s iteration=%s tool=%s",
                            user_id,
                            iteration,
                            tool_call.name
                        )
                        return AgentResponse(
                            message="未找到对应工具",
                            user_id=user_id,
                            intent=intent,
                            execution_path="llm",
                            status="failed",
                            error=f"工具不存在：{tool_call.name}"
                        )

                    logger.info(
                        "tool execution started: user_id=%s iteration=%s tool=%s",
                        user_id,
                        iteration,
                        tool_call.name
                    )

                    tool_result = tool.execute(tool_call.arguments)

                    logger.info(
                        "tool execution completed: user_id=%s iteration=%s tool=%s success=%s",
                        user_id,
                        iteration,
                        tool_call.name,
                        tool_result.success
                    )
                    messages.append(
                        LLMMessage(
                            role=MessageRole.TOOL,
                            content=json.dumps(
                                tool_result.model_dump(),
                                ensure_ascii=False
                            ),
                            tool_call_id=tool_call.id
                        )
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

            logger.exception(
                "llm path execution failed: user_id=%s intent=%s",
                user_id,
                intent
            )

            return AgentResponse(
                message="LLM执行异常",
                user_id=user_id,
                intent=intent,
                execution_path="llm",
                status="failed",
                result=None,
                error=str(e)
            )
