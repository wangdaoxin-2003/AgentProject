import json
from unittest.mock import patch, MagicMock

from rag.doubao_embedding import DoubaoEmbedding


def test_doubao_embedding_success(monkeypatch):
    # 1. 配置测试环境变量
    monkeypatch.setenv("ARK_API_KEY", "fake-key")
    monkeypatch.setenv(
        "ARK_EMBEDDING_MODEL",
        "test-embedding-model"
    )

    # 2. 模拟 API 返回的 JSON
    fake_result = {
        "data": {
            "embedding": [0.1, 0.2, 0.3]
        }
    }

    # 3. 模拟 HTTP 响应
    fake_response = MagicMock()
    fake_response.__enter__.return_value = fake_response
    fake_response.read.return_value = json.dumps(
        fake_result
    ).encode("utf-8")

    # 4. 拦截真实网络调用
    with patch(
            "rag.doubao_embedding.urlopen",
            return_value=fake_response
    ) as mock_urlopen:
        embedding = DoubaoEmbedding()

        vectors = embedding.embed_texts(
            ["住宿费用上限为每晚400元"]
        )

    # 5. 验证返回结果
    assert vectors == [[0.1, 0.2, 0.3]]

    # 6. 验证 HTTP 调用了一次
    mock_urlopen.assert_called_once()
