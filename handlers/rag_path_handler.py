from handlers.base_path_handler import BasePathHandler
from rag.pipeline import RAGPipeline
from schemas import AgentResponse


class RAGPathHandler(BasePathHandler):
    def __init__(self,rag_pipeline:RAGPipeline):
        self.rag_pipeline=rag_pipeline
    def handle(self,message:str,user_id:str,intent:str) ->AgentResponse:
        rag_result=self.rag_pipeline.run(message)
        llm_result=rag_result.llm_result
        sources=[
            chunk.model_dump()
            for chunk in rag_result.sources
        ]
        if llm_result.success:
            return AgentResponse(
                message=rag_result.llm_result.data["content"],
                user_id=user_id,
                intent=intent,
                execution_path="rag",
                status="success",
                result={
                    "sources":sources
                },
                error=None

            )
        return AgentResponse(
            message="RAG执行失败",
            user_id=user_id,
            intent=intent,
            execution_path="rag",
            status="failed",
            result={
                "sources":sources
            },
            error=llm_result.error
        )