import json
import os
from urllib.request import urlopen, Request

from pygments.lexers import data

from rag.base_embedding import BaseEmbedding


class DoubaoEmbedding(BaseEmbedding):
    def __init__(self):
        self.api_key=os.getenv("ARK_API_KEY")
        self.model=os.getenv("ARK_EMBEDDING_MODEL")

        if not self.api_key:
            raise ValueError("ARK_API_KEY 未配置")
        if not self.model:
            raise ValueError("ARK_EMBEDDING_MODEL 未配置")
        self.url=(
            "https://ark.cn-beijing.volces.com"
            "/api/v3/embeddings/multimodal"
        )
    def embed_texts(
            self,
            texts: list[str],
    ) -> list[list[float]]:
            vectors=[]
            for text in texts:
                if not text.strip():
                    raise ValueError("Embedding 输入不能为空")
                payload={
                    "model":self.model,
                    "input":[
                        {
                            "type":"text",
                            "text":text
                        }
                    ],
                    "encoding_format":"float"
                }

                request = Request(
                    url=self.url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization":f"Bearer {self.api_key}",
                        "Content-Type":"application/json"
                    },
                    method="POST"
                )
                with urlopen(request,timeout=30) as response:
                    result=json.load(response)
                vector= result["data"]["embedding"]
                if not isinstance(vector,list) or not vector:
                    raise ValueError("Embedding API 返回无效向量")
                vectors.append([float(value) for value in vector])
            return vectors