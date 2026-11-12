from pydantic import BaseModel, Field

from schemas import LLMResult


class KnowledgeChunk(BaseModel):
    chunk_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source: str = Field(min_length=1)
    section: str | None = None

class RAGResult(BaseModel):
    llm_result:LLMResult
    sources:list[KnowledgeChunk]

