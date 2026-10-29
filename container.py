from conversation import context_window_manager
from conversation.context_window_manager import ContextWindowManager
from conversation.sqlite_history import SQLiteConversationHistory
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
from workflow.engine import WorkflowEngine
from workflow.models import WorkflowStep, Workflow
from workflow.registry import WorkflowRegistry


class ApplicationContainer:
    def create_runtime(self) -> AgentRuntime:
        load_dotenv()
        intent_recognizer = IntentRecognizer()
        path_selector = PathSelector()

        tool_registry = ToolRegistry()
        workflow_engine = WorkflowEngine(
            tool_registry=tool_registry
        )
        workflow_registry = WorkflowRegistry()
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

        double_calculation_workflow = Workflow(
            name="double_calculation",
            steps=[
                WorkflowStep(
                    name="calculate_first",
                    tool_name="calculator",
                    arguments={
                        "expression": "{{expression1}}"
                    }
                ),
                WorkflowStep(
                    name="calculate_second",
                    tool_name="calculator",
                    arguments={
                        "expression": "{{steps.calculate_first.result}}*5"
                    }
                )
            ]

        )
        workflow_registry.register(
            double_calculation_workflow
        )



        prompt_builder = PromptBuilder()
        conversation_history =SQLiteConversationHistory(
            db_path="data/agent_memory.db",
            max_messages=20
        )
        conversation_history.create_table()
        context_window_manager=ContextWindowManager(max_tokens=1000)
        llm_path_handler = LLMPathHandler(
            llm_client=llm_client,prompt_builder=prompt_builder,
            conversation_history=conversation_history,
            tool_registry=tool_registry,
            context_window_manager=context_window_manager
        )
        workflow_path_handler = WorkflowPathHandler(
            workflow_registry=workflow_registry,
            workflow_engine=workflow_engine
        )
        path_handler_registry = PathHandlerRegistry()

        path_handler_registry.register(PathType.FAST, fast_path_handler)
        path_handler_registry.register(PathType.LLM, llm_path_handler)
        path_handler_registry.register(PathType.WORKFLOW, workflow_path_handler)



        return AgentRuntime(
            intent_recognizer=intent_recognizer,
            path_selector=path_selector,
            path_handler_registry=path_handler_registry
        )
