from abc import ABC,abstractmethod
from schemas import AgentResponse

class BasePathHandler(ABC):
    @abstractmethod
    def handle(self,message:str,user_id:str,intent:str)->AgentResponse:
        pass