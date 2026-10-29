import pytest

from rag.base_embedding import BaseEmbedding


def test_base_embedding_cannot_instantiate():
    with pytest.raises(TypeError):
        BaseEmbedding()

def test_embedding_must_implement_method():
    class IncompleteEmbedding(BaseEmbedding):
        pass
    with pytest.raises(TypeError):
        IncompleteEmbedding()