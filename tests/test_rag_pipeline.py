from pathlib import Path

from rag.document_loader import DocumentLoader
from rag.text_splitter import TextSplitter
from rag.chunk_builder import KnowledgeChunkBuilder
from rag.models import KnowledgeChunk


def test_rag_document_pipeline():
    # 1. 定位项目中的模拟制度文件
    project_root = Path(__file__).resolve().parent.parent
    file_path = project_root / "knowledge" / "travel_policy.md"

    # 2. 读取完整制度内容
    loader = DocumentLoader()
    text = loader.load(str(file_path))

    assert "差旅费用管理办法" in text
    assert "每晚400元" in text

    # 3. 创建文本切分器
    splitter = TextSplitter(
        chunk_size=100,
        chunk_overlap=20
    )

    # 4. 创建 ChunkBuilder
    builder = KnowledgeChunkBuilder(
        text_splitter=splitter
    )

    # 5. 把真实文件内容转换成知识片段
    chunks = builder.build(
        text=text,
        document_id="travel_policy",
        source=file_path.name
    )

    # 6. 验证结果不为空
    assert len(chunks) > 0

    # 7. 验证每个对象的类型和来源信息
    assert all(
        isinstance(chunk, KnowledgeChunk)
        for chunk in chunks
    )

    assert all(
        chunk.document_id == "travel_policy"
        for chunk in chunks
    )

    assert all(
        chunk.source == "travel_policy.md"
        for chunk in chunks
    )

    # 8. 验证各个 Chunk 的 ID 不重复
    chunk_ids = [chunk.chunk_id for chunk in chunks]
    assert len(chunk_ids) == len(set(chunk_ids))

    # 9. 验证原文内容得到保留
    combined_text = "".join(chunk.content for chunk in chunks)

    assert "每晚400元" in combined_text