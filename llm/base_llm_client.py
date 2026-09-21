from abc import ABC,abstractmethod
from schemas import LLMResult,LLMMessage
class BaseLLMClient(ABC):
    @abstractmethod
    def chat(self,messages:list[LLMMessage])->LLMResult:
        pass
