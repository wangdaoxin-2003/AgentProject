from pydantic import BaseModel, Field


class KnowledgeChunk(BaseModel):
    chunk_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source: str = Field(min_length=1)
    section: str | None = None
