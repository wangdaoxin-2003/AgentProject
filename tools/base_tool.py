from abc import ABC,abstractmethod#ABC：Abstract Base Class 抽象基类
from schemas import ToolResult
from typing import Any
class BaseTool(ABC):

    name:str
    @abstractmethod#abstractmethod表示这个方法必须被实现
    def execute(self,message:str|dict[str,Any])->ToolResult:#接收字符串、返回一个字典
        pass