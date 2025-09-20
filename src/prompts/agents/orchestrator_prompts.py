# src/prompts/agents/orchestrator_prompts.py
from typing import Dict, Any
from ..base_prompts import StandardPromptTemplate

class OrchestratorPrompts:
    """Prompt builder for Orchestrator Agent"""
    
    @staticmethod
    def create_prompt(context: Dict[str, Any]) -> StandardPromptTemplate:
        """Create orchestrator prompt from YAML template"""
        return StandardPromptTemplate.from_yaml("orchestrator", context)
    
    @staticmethod
    def create_simple_prompt(context: Dict[str, Any]) -> StandardPromptTemplate:
        """Create a simple orchestrator prompt (legacy method)"""
        return StandardPromptTemplate(
            context=f"You are an intelligent orchestrator. Domain: {context.get('domain', 'N/A')}, Project: {context.get('project_name', 'N/A')}",
            task="Analyze requirements and delegate tasks to specialized agents",
            constraints="Maintain context, ensure quality, follow workflow phases",
            output_format='{"analysis": "string", "next_phase": "string", "delegated_tasks": ["string"], "success": boolean}'
        )
