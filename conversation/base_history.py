from abc import abstractmethod, ABC

from schemas import LLMMessage


class BaseConversationHistory(ABC):

    @abstractmethod
    def add_message(self,user_id:str,message:LLMMessage)->None:
        pass
    @abstractmethod
    def get_history(self,user_id:str)->list[LLMMessage]:
        pass