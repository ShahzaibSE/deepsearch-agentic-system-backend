from config._agents.base_agent import BaseAgentBuilder
from agents import Agent, AsyncOpenAI, ModelSettings

class RequirementGathererAgent(BaseAgentBuilder):
    _instance = None
    _agent_instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, client: AsyncOpenAI, agent_name: str, model_settings: ModelSettings):
        if not self._initialized:
            super().__init__(client, agent_name, model_settings)
            self._initialized = True
    
    def create_agent(self) -> Agent:
        if not self._agent_instance:
            self._agent_instance = Agent(
                name=self.agent_name,
                model=self.client,
                model_settings=self.model_settings
            )
        return self._agent_instance