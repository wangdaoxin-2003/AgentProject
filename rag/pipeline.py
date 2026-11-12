from llm.base_llm_client import BaseLLMClient
from rag import retriever
from rag.rag_context_builder import RAGContextBuilder
from rag.models import RAGResult
from rag.rag_prompt_builder import RAGPromptBuilder
from rag.retriever import Retriever
from schemas import LLMResult


class RAGPipeline:
    def __init__(
            self,
            retriever:Retriever,
            context_builder:RAGContextBuilder,
            prompt_builder:RAGPromptBuilder,
            llm_client:BaseLLMClient

    ):
        self.retriever=retriever
        self.context_builder=context_builder
        self.prompt_builder=prompt_builder
        self.llm_client=llm_client
    def run(
            self,
            query:str,
            top_k:int=3,
    )->RAGResult:
        try:
            records = self.retriever.retrieve(query, top_k)
            sources = [record.chunk for record in records]
        except ValueError as exc:
            return RAGResult(
                llm_result=LLMResult(
                model="failing-mock",
                success=False,
                tool_calls=None,
                data=None,
                usage=None,
                error=str(exc)
                ),
                sources=[]
            )
        context = self.context_builder.build(records)
        messages=self.prompt_builder.build(query,context)
        llm_result=self.llm_client.chat(messages)
        return RAGResult(
            llm_result=llm_result,
            sources=sources
        )