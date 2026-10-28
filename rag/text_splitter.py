


class TextSplitter:
    def __init__(
        self,
        chunk_size: int = 200,
        chunk_overlap: int = 40
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size 必须大于0")

        if not 0 <= chunk_overlap < chunk_size:
            raise ValueError(
                "chunk_overlap 必须大于等于0且小于chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[str]:
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = min(
                start + self.chunk_size,
                len(text)
            )

            chunks.append(text[start:end])

            if end == len(text):
                break

            start = end - self.chunk_overlap

        return chunks


