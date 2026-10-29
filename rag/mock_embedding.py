from rag.base_embedding import BaseEmbedding


class MockEmbedding(BaseEmbedding):
    def embed_texts(
            self,
            texts:list[str],
    )->list[list[str]]:
        vectors =[]

        for text in texts:
            vector=[
                float(len(text)),
                float(sum(ord(char) for char in text) %100),
                float(len(set(text)))
            ]
            vectors.append(vector)
        return vectors
