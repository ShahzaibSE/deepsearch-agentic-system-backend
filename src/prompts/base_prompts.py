# src/prompts/base_prompts.py
import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any, Optional

class PromptTemplateLoader(BaseModel):
    """Loads and manages YAML prompt templates"""
    
    templates_dir: Path = Path(__file__).parent / "templates"
    
    def load_template(self, agent_name: str) -> Dict[str, str]:
        """Load YAML template for a specific agent"""
        template_path = self.templates_dir / f"{agent_name}.yaml"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def render_template(self, agent_name: str, context: Dict[str, Any]) -> str:
        """Load template and render with context data"""
        template = self.load_template(agent_name)
        
        rendered_parts = []
        
        # Render each section with context
        for section, content in template.items():
            if isinstance(content, str):
                rendered_content = content.format(**context)
                rendered_parts.append(f"## {section.replace('_', ' ').title()}\n{rendered_content}\n")
        
        return "\n".join(rendered_parts)

class StandardPromptTemplate(BaseModel):
    """Fixed template structure for all agents"""
    
    # Fixed sections - always present
    context: str
    task: str
    constraints: str
    output_format: str
    
    # Optional sections
    examples: Optional[str] = None
    tools_available: Optional[str] = None
    handoff_instructions: Optional[str] = None
    
    def render(self) -> str:
        """Render the complete prompt"""
        prompt_parts = [
            f"## Context\n{self.context}\n",
            f"## Task\n{self.task}\n",
            f"## Constraints\n{self.constraints}\n",
            f"## Output Format\n{self.output_format}\n"
        ]
        
        if self.examples:
            prompt_parts.append(f"## Examples\n{self.examples}\n")
        
        if self.tools_available:
            prompt_parts.append(f"## Available Tools\n{self.tools_available}\n")
        
        if self.handoff_instructions:
            prompt_parts.append(f"## Handoff Instructions\n{self.handoff_instructions}\n")
        
        return "\n".join(prompt_parts)
    
    @classmethod
    def from_yaml(cls, agent_name: str, context: Dict[str, Any]) -> 'StandardPromptTemplate':
        """Create template from YAML file with context"""
        loader = PromptTemplateLoader()
        template_data = loader.load_template(agent_name)
        
        # Convert template data to StandardPromptTemplate
        return cls(
            context=template_data.get('context', '').format(**context),
            task=template_data.get('task', '').format(**context),
            constraints=template_data.get('constraints', '').format(**context),
            output_format=template_data.get('output_format', '').format(**context),
            examples=template_data.get('examples', '').format(**context) if template_data.get('examples') else None,
            tools_available=template_data.get('tools_available', '').format(**context) if template_data.get('tools_available') else None,
            handoff_instructions=template_data.get('handoff_instructions', '').format(**context) if template_data.get('handoff_instructions') else None
        )