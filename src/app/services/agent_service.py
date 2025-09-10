from config._agents.orchestrator_agent import OrchestratorAgent
from config.llm_configs.gemini_model import GeminiConfig
from config.settings import settings
from agents import RunContextWrapper

class AgentService:
    def __init__(self):
        self.orchestrator_agent = OrchestratorAgent(
            client=GeminiConfig().get_client(),
            agent_name="orchestrator",
            model_settings=GeminiConfig().create_model_settings()
        ).create_agent()
    
    async def execute_with_handoffs(self, task: str, context: dict):
            """Execute task allowing agents to handoff to each other"""
            pass