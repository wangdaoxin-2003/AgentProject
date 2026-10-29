from rag.chunk_builder import KnowledgeChunkBuilder
from rag.models import KnowledgeChunk
from rag.text_splitter import TextSplitter


def test_build_knowledge_chunks():
    splitter = TextSplitter(
        chunk_size=6,
        chunk_overlap=2
    )

    builder = KnowledgeChunkBuilder(
        text_splitter=splitter
    )

    chunks = builder.build(
        text="ABCDEFGHIJ",
        document_id="travel_policy",
        source="travel_policy.md"
    )

    # 1. 验证返回两个片段
    assert len(chunks) == 2

    # 2. 验证返回 KnowledgeChunk 对象
    assert all(
        isinstance(chunk, KnowledgeChunk)
        for chunk in chunks
    )

    # 3. 验证内容正确
    assert chunks[0].content == "ABCDEF"
    assert chunks[1].content == "EFGHIJ"

    # 4. 验证片段 ID
    assert chunks[0].chunk_id == "travel_policy_1"
    assert chunks[1].chunk_id == "travel_policy_2"

    # 5. 验证来源信息
    assert chunks[0].document_id == "travel_policy"
    assert chunks[1].source == "travel_policy.md"


def test_build_empty_text():
    builder = KnowledgeChunkBuilder(
        text_splitter=TextSplitter()
    )

    chunks = builder.build(
        text="",
        document_id="travel_policy",
        source="travel_policy.md"
    )

    assert chunks == []