from rag.models import KnowledgeChunk
from rag.text_splitter import TextSplitter


class KnowledgeChunkBuilder:
    def __init__(self,text_splitter:TextSplitter):
        self.text_splitter = text_splitter
    def build(
            self,
            text:str,
            document_id:str,
            source:str
    ) ->list[KnowledgeChunk]:
        texts=self.text_splitter.split(text)

        chunks=[]
        for index,content in enumerate(texts,start=1):
            chunk= KnowledgeChunk(
                chunk_id=f"{document_id}_{index}",
                document_id=document_id,
                content=content,
                source=source,
                section=None
            )
            chunks.append(chunk)
        return chunks

