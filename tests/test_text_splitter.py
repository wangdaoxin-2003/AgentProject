import pytest

from rag.text_splitter import TextSplitter


def test_split_with_overlap():
    splitter = TextSplitter(
        chunk_size=8,
        chunk_overlap=2
    )

    chunks = splitter.split("ABCDEFGHIJKLMN")

    assert chunks == [
        "ABCDEFGH",
        "GHIJKLMN"
    ]


def test_split_short_text():
    splitter = TextSplitter(
        chunk_size=10,
        chunk_overlap=2
    )

    chunks = splitter.split("你好")

    assert chunks == ["你好"]


def test_split_empty_text():
    splitter = TextSplitter()

    assert splitter.split("") == []


def test_invalid_overlap():
    with pytest.raises(ValueError):
        TextSplitter(
            chunk_size=5,
            chunk_overlap=5
        )
def test_split_with_overlap():
    splitter = TextSplitter(
        chunk_size=8,
        chunk_overlap=2
    )

    chunks = splitter.split("ABCDEFGHIJKLMN")

    assert chunks == [
        "ABCDEFGH",
        "GHIJKLMN"
    ]


def test_split_short_text():
    splitter = TextSplitter(
        chunk_size=10,
        chunk_overlap=2
    )

    chunks = splitter.split("你好")

    assert chunks == ["你好"]


def test_split_empty_text():
    splitter = TextSplitter()

    assert splitter.split("") == []


def test_invalid_overlap():
    with pytest.raises(ValueError):
        TextSplitter(
            chunk_size=5,
            chunk_overlap=5
        )