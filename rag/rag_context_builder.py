from rag.vector_store import VectorRecord


class RAGContextBuilder:

    def build(
        self,
        records: list[VectorRecord]
    ) -> str:
        parts=[]
        # 1. 遍历 records
        for index,record in enumerate(records,start=1):

            # 2. 获取每条记录的 source 和 content
            source = f"[{index}] 来源：{record.chunk.source}\n"
            content = f"[{index}] 内容：{record.chunk.content}\n"
            # 3. 将来源和内容格式化为字符串
            part=source+content
            # 4. 将字符串添加到 parts
            parts.append(part)
        # 5. 把 parts 合并为一个字符串并返回
        return "\n\n".join(parts)