from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class Project(BaseModel):
    """Persistent project data"""
    id: str = Field(..., description="Unique project identifier")
    domain: str = Field(..., description="Business domain")
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    status: str = Field(..., description="Project status")
    owner: str = Field(..., description="Project owner")
    owner_email: str = Field(..., description="Project owner email")
    created_at: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))

class AgentContext(BaseModel):
    """Local context for agent runs (ephemeral)"""
    # Project reference
    # project_id: str = Field(..., description="Reference to persistent project")
    
    # Runtime state
    # current_phase: str = Field(..., description="Current workflow phase")
    # agent_run_id: str = Field(..., description="Unique run identifier")
    
    # Cached project data (for performance)
    domain: str = Field(..., description="Domain")
    project_name: str = Field(..., description="Project name")
    project_description: str = Field(..., description="Project description")
    
    # Runtime metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Runtime metadata")
    
    # Runtime timestamps
    run_started_at: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))