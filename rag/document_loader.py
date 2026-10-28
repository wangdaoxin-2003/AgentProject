
from pathlib import Path


class DocumentLoader:
    def load(self,file_path:str) ->str:

        path=Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"文件不存在：{file_path}"
            )
        if path.suffix.lower() !=".md":
            raise ValueError("当前只支持Markdown文件")
        return path.read_text(encoding="utf-8")