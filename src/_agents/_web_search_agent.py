from agents import Agent, AsyncOpenAI, ModelSettings, AsyncOpenAI, set_tracing_disabled
from dotenv import load_dotenv
from pathlib import Path
import os
from _base_agent import BaseAgentBuilder

class WebSearchAgent(BaseAgentBuilder):
    
    def __init__(self, client, agent_name: str, model_settings: ModelSettings):
        super().__init__(client, agent_name, model_settings)
    
    async def createAgent(self):
        return Agent(
            name= self.agent_name,
            model= self.client,
            model_settings= self.model_settings
        )
