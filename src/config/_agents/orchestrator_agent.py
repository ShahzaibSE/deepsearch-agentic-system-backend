from base_agent import BaseAgentBuilder
from agents import Agent, AsyncOpenAI, ModelSettings

class OrchestratorAgent(BaseAgentBuilder):
    def __init__(self, client: AsyncOpenAI, agent_name: str, model_settings: ModelSettings):
        super().__init__(client, agent_name, model_settings)

    def create_agent(self) -> Agent:
        return Agent(
            name=self.agent_name,
            model=self.client,
            model_settings=self.model_settings)