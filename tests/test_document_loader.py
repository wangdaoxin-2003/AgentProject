import pytest

from rag.document_loader import DocumentLoader


def test_load_markdown_success():
    loader = DocumentLoader()

    content = loader.load(
        "knowledge/travel_policy.md"
    )

    assert isinstance(content, str)
    assert "差旅费用管理办法" in content
    assert "每晚400元" in content


def test_load_file_not_found():
    loader = DocumentLoader()

    with pytest.raises(FileNotFoundError):
        loader.load(
            "knowledge/not_exists.md"
        )


def test_load_unsupported_file(tmp_path):
    loader = DocumentLoader()

    file_path = tmp_path / "test.txt"
    file_path.write_text("测试内容", encoding="utf-8")

    with pytest.raises(ValueError):
        loader.load(str(file_path))