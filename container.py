from conversation.history import ConversationHistory
from handlers.fast_path_handler import FastPathHandler
from handlers.llm_path_handler import LLMPathHandler
from handlers.workflow_path_handler import WorkflowPathHandler
from intent import IntentRecognizer
from path_handler_registry import PathHandlerRegistry
from path_selector import PathSelector, PathType
from prompt.prompt_builder import PromptBuilder
from runtime import AgentRuntime
from tool_registry import ToolRegistry
import os
from dotenv import load_dotenv
from llm.doubao_llm_client import DoubaoLLMClient
from llm.mock_llm_client import MockLLMClient


class ApplicationContainer:
    def create_runtime(self) -> AgentRuntime:
        load_dotenv()
        intent_recognizer = IntentRecognizer()
        path_selector = PathSelector()

        tool_registry = ToolRegistry()
        fast_path_handler = FastPathHandler(tool_registry=tool_registry)
        # llm_client = DoubaoLLMClient()
        llm_provider=os.getenv(
            "LLM_PROVIDER",
            "mock"
        ).lower()
        if llm_provider=="doubao":
            llm_client = DoubaoLLMClient()
        elif llm_provider=="mock":
            llm_client = MockLLMClient()
        else:
            raise ValueError(
                f"不支持的LLM_PROVIDER：{llm_provider}"
            )
        prompt_builder = PromptBuilder()
        conversation_history = ConversationHistory()
        llm_path_handler = LLMPathHandler(llm_client=llm_client,prompt_builder=prompt_builder, conversation_history=conversation_history,tool_registry=tool_registry)
        workflow_path_handler = WorkflowPathHandler()
        path_handler_registry = PathHandlerRegistry()

        path_handler_registry.register(PathType.FAST, fast_path_handler)
        path_handler_registry.register(PathType.LLM, llm_path_handler)
        path_handler_registry.register(PathType.WORKFLOW, workflow_path_handler)


        return AgentRuntime(
            intent_recognizer=intent_recognizer,
            path_selector=path_selector,
            path_handler_registry=path_handler_registry
        )
