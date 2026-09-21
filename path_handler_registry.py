from path_selector import PathType
from handlers.base_path_handler import BasePathHandler
class PathHandlerRegistry:
    def __init__(self):
        self._handlers:dict[PathType,BasePathHandler]={}
    def register(self,path_type:PathType,handler:BasePathHandler) -> None:
        self._handlers[path_type] =handler
    def get_handler(self,path_type:PathType) -> BasePathHandler | None:
        return self._handlers.get(path_type)