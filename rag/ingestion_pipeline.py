from rag.document_loader import DocumentLoader
from rag.chunk_builder import KnowledgeChunkBuilder
from rag.base_embedding import BaseEmbedding
from rag.models import KnowledgeChunk
from rag.vector_store import InMemoryVectorStore, VectorRecord


class KnowledgeIngestionPipeline:

    def __init__(
        self,
        document_loader: DocumentLoader,
        chunk_builder: KnowledgeChunkBuilder,
        embedding: BaseEmbedding,
        vector_store: InMemoryVectorStore
    ):
        self.document_loader = document_loader
        self.chunk_builder = chunk_builder
        self.embedding = embedding
        self.vector_store = vector_store

    def ingest(
            self,
            file_path: str,
            document_id: str
    ) -> list[KnowledgeChunk]:
        # 第一步：读取文件
        text = self.document_loader.load(file_path)

        if not text.strip():
            return []

        # 第二步：构建知识块
        chunks = self.chunk_builder.build(
            text=text,
            document_id=document_id,
            source=file_path
        )
        texts=[
            chunk.content for chunk in chunks
        ]
        vectors=self.embedding.embed_texts(texts)
        """知识块与向量的对应关系
        KnowledgeChunk：员工每年享有5天年假
        Embedding Vector：[0.12, 0.38, 0.91]
        VectorRecord：chunk+vector负责将一段只是及其向量绑定在一起

        """
        if len(chunks)!=len(vectors):
            raise ValueError("知识块数量与向量数量不一致")
        for chunk,vector in zip(chunks,vectors):
            record=VectorRecord(
                chunk=chunk,
                vector=vector
            )
            self.vector_store.add_record(record)
        return chunks # 附加回执