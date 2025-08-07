from abc import ABC, abstractmethod

class BaseModelConfig(ABC):
    
    def __init__(self, api_key_env_var):
        self.api_key = api_key_env_var
        
        if not self.api_key:
           raise ValueError(f"{self.api_key_env_var} is not set in the environment.")
       
    @property
    @abstractmethod
    def get_api_key(self) -> str:
        pass   


    @abstractmethod
    def get_chat_completion(self, messages: list[dict]) -> str:
        pass