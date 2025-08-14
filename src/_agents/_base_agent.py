from abc import ABC, abstractmethod
from agents import Agent, AsyncOpenAI, ModelSettings

class BaseAgentBuilder(ABC):
    def __init__(self, client: AsyncOpenAI, agent_name: str, model_settings: ModelSettings):
        self.agent_name = agent_name
        self.client = client
        self.model_settings = model_settings
        
    @abstractmethod
    async def createAgent(self) -> Agent:
        pass