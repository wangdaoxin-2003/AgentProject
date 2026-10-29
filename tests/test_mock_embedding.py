from rag.base_embedding import BaseEmbedding
from rag.mock_embedding import MockEmbedding


def test_mock_embedding_implements_interface():
    embedding = MockEmbedding()

    assert isinstance(embedding, BaseEmbedding)


def test_mock_embedding_vectors():
    embedding = MockEmbedding()

    vectors = embedding.embed_texts([
        "ABC",
        "AB"
    ])

    assert vectors == [
        [3.0, 98.0, 3.0],
        [2.0, 31.0, 2.0]
    ]


def test_mock_embedding_deterministic():
    embedding = MockEmbedding()

    result1 = embedding.embed_texts(["报销制度"])
    result2 = embedding.embed_texts(["报销制度"])

    assert result1 == result2


def test_mock_embedding_empty_input():
    embedding = MockEmbedding()

    assert embedding.embed_texts([]) == []