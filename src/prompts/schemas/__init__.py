# src/prompts/schemas/__init__.py
"""
XSD Schema definitions for prompt templates
"""

from pathlib import Path

# Schema file paths
SCHEMA_DIR = Path(__file__).parent
PROMPT_SCHEMA_PATH = SCHEMA_DIR / "prompt_schema.xsd"

__all__ = [
    "SCHEMA_DIR",
    "PROMPT_SCHEMA_PATH"
]
