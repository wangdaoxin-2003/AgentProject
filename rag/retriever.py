from rag.base_embedding import BaseEmbedding
from rag.vector_store import InMemoryVectorStore, VectorRecord


class Retriever:
    def __init__(
            self,
            embedding: BaseEmbedding,
            vector_store: InMemoryVectorStore
    ):
        self.embedding = embedding
        self.vector_store = vector_store

    def retrieve(
            self,
            query: str,
            top_k: int = 3
    ) -> list[VectorRecord]:
        vectors = self.embedding.embed_texts([query])
        if not vectors:
            raise ValueError("未返回查询向量")
        query_vector = vectors[0]
        return self.vector_store.search(query_vector=query_vector, top_k=top_k)
