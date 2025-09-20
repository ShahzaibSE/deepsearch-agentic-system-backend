# src/prompts/_agents/search_prompts.py
from typing import Dict, Any
from ..base_prompts import StandardPromptTemplate

class SearchPrompts:
    """Prompt builder for Search Agent"""
    
    @staticmethod
    def create_prompt(context: Dict[str, Any]) -> StandardPromptTemplate:
        """Create search agent prompt from YAML template"""
        return StandardPromptTemplate.from_yaml("search_agent", context)
    
    @staticmethod
    def create_simple_prompt(context: Dict[str, Any]) -> StandardPromptTemplate:
        """Create a simple search agent prompt (legacy method)"""
        return StandardPromptTemplate(
            context=f"You are a web search specialist for {context.get('domain', 'N/A')} projects",
            task="Perform targeted web searches to gather relevant information",
            constraints="Focus on domain relevance, prioritize recent sources, verify accuracy",
            output_format='{"search_results": [{"title": "string", "url": "string", "summary": "string", "relevance_score": number}], "key_insights": ["string"], "trends": ["string"], "recommendations": ["string"], "search_quality": number}'
        )
