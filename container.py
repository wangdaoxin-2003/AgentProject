from pathlib import Path

from conversation import context_window_manager
from conversation.context_window_manager import ContextWindowManager
from conversation.sqlite_history import SQLiteConversationHistory
from handlers.fast_path_handler import FastPathHandler
from handlers.llm_path_handler import LLMPathHandler
from handlers.rag_path_handler import RAGPathHandler
from handlers.workflow_path_handler import WorkflowPathHandler
from intent import IntentRecognizer
from path_handler_registry import PathHandlerRegistry
from path_selector import PathSelector, PathType
from prompt.prompt_builder import PromptBuilder
from rag import retriever, document_loader, text_splitter, chunk_builder
from rag.chunk_builder import KnowledgeChunkBuilder
from rag.rag_context_builder import RAGContextBuilder
from rag.document_loader import DocumentLoader
from rag.doubao_embedding import DoubaoEmbedding
from rag.ingestion_pipeline import KnowledgeIngestionPipeline
from rag.mock_embedding import MockEmbedding
from rag.pipeline import RAGPipeline
from rag.rag_prompt_builder import RAGPromptBuilder
from rag.retriever import Retriever
from rag.text_splitter import TextSplitter
from rag.vector_store import InMemoryVectorStore
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
        llm_provider = os.getenv(
            "LLM_PROVIDER",
            "mock"
        ).lower()
        if llm_provider == "doubao":
            llm_client = DoubaoLLMClient()
        elif llm_provider == "mock":
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
        conversation_history = SQLiteConversationHistory(
            db_path="data/agent_memory.db",
            max_messages=20
        )
        conversation_history.create_table()
        context_window_manager = ContextWindowManager(max_tokens=1000)
        llm_path_handler = LLMPathHandler(
            llm_client=llm_client, prompt_builder=prompt_builder,
            conversation_history=conversation_history,
            tool_registry=tool_registry,
            context_window_manager=context_window_manager
        )
        workflow_path_handler = WorkflowPathHandler(
            workflow_registry=workflow_registry,
            workflow_engine=workflow_engine
        )

        embedding_provider =os.getenv(
            "EMBEDDING_PROVIDER",
            "mock"
        ).lower()
        if embedding_provider=="doubao":
            rag_embedding =DoubaoEmbedding()
        elif embedding_provider =="mock":
            rag_embedding=MockEmbedding()
        else:
            raise ValueError(f"不支持的 EMBEDDING_PROVIDER {embedding_provider}")

        vector_store = InMemoryVectorStore()
        retriever = Retriever(
            embedding=rag_embedding,
            vector_store=vector_store
        )
        rag_context_builder = RAGContextBuilder()
        rag_prompt_builder = RAGPromptBuilder()
        rag_pipeline = RAGPipeline(
            retriever=retriever,
            context_builder=rag_context_builder,
            prompt_builder=rag_prompt_builder,
            llm_client=llm_client
        )

        document_loader=DocumentLoader()
        text_splitter = TextSplitter(
            chunk_size=200,
            chunk_overlap=40
        )
        chunk_builder=KnowledgeChunkBuilder(
            text_splitter=text_splitter
        )

        ingestion_pipeline=KnowledgeIngestionPipeline(
            document_loader=document_loader,
            chunk_builder=chunk_builder,
            embedding=rag_embedding,
            vector_store=vector_store
        )
        knowledge_path=(
            Path(__file__).resolve().parent
            / "knowledge"
            / "travel_policy.md"
        )
        chunks=ingestion_pipeline.ingest(
            file_path=str(knowledge_path),
            document_id="travel_policy"
        )
        print(f"知识库初始化完成：{len(chunks)} 个知识块")
        rag_path_handler = RAGPathHandler(
            rag_pipeline=rag_pipeline
        )
        path_handler_registry = PathHandlerRegistry()

        path_handler_registry.register(PathType.FAST, fast_path_handler)
        path_handler_registry.register(PathType.LLM, llm_path_handler)
        path_handler_registry.register(PathType.WORKFLOW, workflow_path_handler)
        path_handler_registry.register(PathType.RAG, rag_path_handler)

        return AgentRuntime(
            intent_recognizer=intent_recognizer,
            path_selector=path_selector,
            path_handler_registry=path_handler_registry
        )
