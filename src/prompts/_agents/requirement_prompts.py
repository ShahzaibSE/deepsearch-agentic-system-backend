# src/prompts/_agents/requirement_prompts.py
from typing import Dict, Any
from ..base_prompts import StandardPromptTemplate

class RequirementGathererPrompts:
    """Prompt builder for Requirement Gatherer Agent"""
    
    @staticmethod
    def create_prompt(context: Dict[str, Any]) -> StandardPromptTemplate:
        """Create requirement gatherer prompt from YAML template"""
        return StandardPromptTemplate.from_yaml("requirement_gatherer", context)
    
    @staticmethod
    def create_simple_prompt(context: Dict[str, Any]) -> StandardPromptTemplate:
        """Create a simple requirement gatherer prompt (legacy method)"""
        return StandardPromptTemplate(
            context=f"You are a requirement gathering specialist for {context.get('domain', 'N/A')} projects",
            task="Research and gather comprehensive project requirements",
            constraints="Focus on domain expertise, ensure accuracy, consider compliance",
            output_format='{"domain_standards": ["string"], "regulatory_requirements": ["string"], "technical_constraints": ["string"], "business_requirements": ["string"], "recommendations": ["string"], "confidence_score": number}'
        )
