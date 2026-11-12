import pytest

from llm.base_llm_client import BaseLLMClient
from llm.mock_llm_client import MockLLMClient
from rag.rag_context_builder import RAGContextBuilder
from rag.models import KnowledgeChunk
from rag.pipeline import RAGPipeline
from rag.rag_prompt_builder import RAGPromptBuilder
from rag.retriever import Retriever
from rag.vector_store import InMemoryVectorStore, VectorRecord
from schemas import LLMMessage, LLMResult
from rag.base_embedding import BaseEmbedding
from workflow_practice.test_step_reference import result


class RecordingLLMClient(MockLLMClient):

    def __init__(self):
        super().__init__()
        self.received_messages = []

    def chat(self, messages: list[LLMMessage]) -> LLMResult:
        # 1. 保存本次传入的 messages
        self.received_messages=messages.copy()
        # 2. 调用父类 MockLLMClient.chat()
        return super().chat(messages)
        # 3. 返回父类的执行结果


class FixedEmbedding(BaseEmbedding):
    def embed_texts(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]
def test_rag_pipeline_success():
    embedding = FixedEmbedding()
    store = InMemoryVectorStore()

    chunk = KnowledgeChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        content="员工入职满一年后享有5天年假。",
        source="employee_rules.md"
    )

    record = VectorRecord(
        chunk=chunk,
        vector=[1.0, 0.0]
    )

    store.add_record(record)
    retriever = Retriever(
        embedding=embedding,
        vector_store=store
    )

    context_builder = RAGContextBuilder()
    prompt_builder = RAGPromptBuilder()
    llm_client = RecordingLLMClient()
    pipeline = RAGPipeline(
       retriever=retriever,
        context_builder=context_builder,
        prompt_builder=prompt_builder,
        llm_client=llm_client
    )
    result=pipeline.run(query="公司年假有多少天？",top_k=1)
    contents = [
        message.content or ""
        for message in llm_client.received_messages
    ]
    assert result.llm_result.success is True
    assert len(result.sources) == 1
    assert result.sources[0].source == "employee_rules.md"
    assert "employee_rules.md" in contents[1]
    assert "员工入职满一年后享有5天年假" in contents[1]
    assert "公司年假有多少天？" in contents[2]
class FailingLLMClient(BaseLLMClient):

    def chat(self, messages: list[LLMMessage]) -> LLMResult:
        return LLMResult(
            model="failing-mock",
            success=False,
            data=None,
            tool_calls=[],
            usage=None,
            error="模拟LLM调用失败"
        )
def test_rag_pipeline_llm_failure():
    embedding = FixedEmbedding()
    store = InMemoryVectorStore()

    retriever = Retriever(
        embedding=embedding,
        vector_store=store
    )

    context_builder = RAGContextBuilder()
    prompt_builder = RAGPromptBuilder()
    llm_client = FailingLLMClient()

    # 1. 创建 RAGPipeline，注入四个依赖
    pipeline=RAGPipeline(
        retriever=retriever,
        context_builder=context_builder,
        prompt_builder=prompt_builder,
        llm_client=llm_client
    )

    # 2. 调用 pipeline.run()
    result = pipeline.run(query="", top_k=1)
    # 3. 检查返回的 LLMResult
    assert result.llm_result.success is False
    assert result.llm_result.error == "模拟LLM调用失败"
class FailingRetriever(Retriever):

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> list[VectorRecord]:

        raise ValueError("检索失败")
def test_rag_pipeline_retriever_failure():
    embedding = FixedEmbedding()
    store = InMemoryVectorStore()

    retriever = FailingRetriever(
        embedding=embedding,
        vector_store=store
    )

    context_builder = RAGContextBuilder()
    prompt_builder = RAGPromptBuilder()
    llm_client = RecordingLLMClient()

    # 1. 创建 RAGPipeline
    pipeline=RAGPipeline(
        retriever=retriever,
        context_builder=context_builder,
        prompt_builder=prompt_builder,
        llm_client=llm_client
    )
    # 2. 调用 pipeline.run()

    # 3. 使用 pytest.raises() 验证 ValueError
    result =pipeline.run("测试问题")
    assert result.llm_result.success is False
    assert result.llm_result.error =="检索失败"
    assert result.sources==[]
def test_rag_pipeline_empty_knowledge():
    embedding = FixedEmbedding()
    store = InMemoryVectorStore()

    # 不调用 store.add_record()
    # 保持知识库为空

    retriever = Retriever(
        embedding=embedding,
        vector_store=store
    )

    context_builder = RAGContextBuilder()
    prompt_builder = RAGPromptBuilder()
    llm_client = RecordingLLMClient()

    # 1. 创建 RAGPipeline
    pipeline = RAGPipeline(
        retriever=retriever,
        context_builder=context_builder,
        prompt_builder=prompt_builder,
        llm_client=llm_client
    )
    # 2. 调用 pipeline.run()
    pipeline.run(query="公司明年涨多少工资？",top_k=3)
    # 3. 验证 LLM 收到无参考资料提示
    contents = [
        message.content or ""
        for message in llm_client.received_messages
    ]
    assert "当前没有检索到可用的参考资料" in contents[1]