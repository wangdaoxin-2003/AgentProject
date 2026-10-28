import pytest
from pydantic import ValidationError

from rag.models import KnowledgeChunk


def test_knowledge_chunk_success():
    chunk=KnowledgeChunk(
        chunk_id="travel_001",
        document_id="travel_policy",
        content="住宿费用按照员工职级执行相应标准",
        source="差旅费用管理办法.md",
        section="第三条"
    )

    assert chunk.chunk_id == "travel_001"
    assert chunk.document_id == "travel_policy"
    assert chunk.section == "第三条"
def test_knowledge_chunk_empty_content():
    with pytest.raises(ValidationError):
        KnowledgeChunk(
            chunk_id="travel_002",
            document_id="travel_policy",
            content="",
            source="差旅费用管理办法.md"
        )