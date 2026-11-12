import math
from pydantic import BaseModel

from rag.models import KnowledgeChunk


class VectorRecord(BaseModel):
    chunk: KnowledgeChunk
    vector: list[float]


class InMemoryVectorStore:
    def __init__(self):
        self.records: list[VectorRecord] = []

    def add_record(self, record: VectorRecord) -> None:
        # 将 record 保存到 self.records
        self.records.append(record)

    def get_all_records(self) -> list[VectorRecord]:
        return self.records.copy()

    def search(self,
               query_vector: list[float],
               top_k: int = 3
               ) -> list[VectorRecord]:
        if top_k <= 0:
            raise ValueError("top_k 必须大于0")
        scored = []
        # 3. 遍历self.record
        # 4. 使用 cosine_similarity()计算分数
        # 5. 按照相似度降序排列
        # 6. 取前 top_k 条并返回对应的VectortorRecord
        for record in self.records:
            score = cosine_similarity(query_vector, record.vector)
            scored.append((score, record))

        scored.sort(key=lambda item: item[0], reverse=True)

        top_records = [item[1] for item in scored[:top_k]]
        return top_records

def cosine_similarity(
        a: list[float],
        b: list[float]
) -> float:
    if not a or not b:
        raise ValueError("向量不能为空")
    if len(a) != len(b):
        raise ValueError("向量维度不一致")
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    if magnitude_a == 0 or magnitude_b == 0:
        raise ValueError("向量长度为0")
    return dot_product / (magnitude_a * magnitude_b)
