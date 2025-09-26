# src/prompts/base_prompts.py
import xml.etree.ElementTree as ET
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any, Optional
from lxml import etree

class PromptTemplateLoader(BaseModel):
    """Loads and manages XML prompt templates with XSD validation"""
    
    templates_dir: Path = Path(__file__).parent / "templates"
    schema_path: Path = Path(__file__).parent / "schemas" / "prompt_schema.xsd"
    
    def validate_template(self, template_path: Path) -> bool:
        """Validate XML template against XSD schema"""
        try:
            schema = etree.XMLSchema(file=str(self.schema_path))
            parser = etree.XMLParser(resolve_entities=False)
            xml_doc = etree.parse(str(template_path), parser)
            schema.assertValid(xml_doc)
            return True
        except etree.XMLSyntaxError as e:
            raise ValueError(f"XML syntax error in template {template_path.name}: {e}")
        except etree.DocumentInvalid as e:
            raise ValueError(f"Schema validation failed for template {template_path.name}: {e}")
        except Exception as e:
            raise ValueError(f"Template validation error for {template_path.name}: {e}")
    
    def load_template(self, agent_name: str) -> Dict[str, str]:
        """Load XML template for a specific agent with validation"""
        template_path = self.templates_dir / f"{agent_name}.xml"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        # Validate template against schema
        self.validate_template(template_path)
        
        # Parse XML template
        tree = ET.parse(template_path)
        root = tree.getroot()
        
        template_data = {}
        for child in root:
            template_data[child.tag] = child.text.strip() if child.text else ""
        
        return template_data
    
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
    def from_xml(cls, agent_name: str, context: Dict[str, Any]) -> 'StandardPromptTemplate':
        """Create template from XML file with context"""
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