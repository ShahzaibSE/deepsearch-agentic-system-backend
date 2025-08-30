from __future__ import annotations
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os
from fastapi import HTTPException
from typing import Dict, Any, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from agents import ModelSettings, AsyncOpenAI

class ModelConfig(BaseModel):
    model_name: str
    model_settings: 'ModelSettings'  # Forward reference
    client: 'AsyncOpenAI'            # Forward reference
    api_key: str

class BaseModelConfig(ABC):
    
    def __init__(self, api_key_env_var):
        self.api_key = api_key_env_var
        
        if not self.api_key:
           raise ValueError(f"{api_key_env_var} is not set in the environment.")
       
    @property
    async def get_api_key(self) -> str:
        """
        Get the API key to make http calls to the LLM
        """   
        try:
            return self.api_key
        except HTTPException as e:
            raise HTTPException(status_code=500, detail=f"Error getting API key: {e}")

    @abstractmethod
    def get_client(self):
        """Get the configured model/client"""
        pass
    
    @abstractmethod
    def get_model_config(self, **params) -> 'ModelConfig':
        """Get the complete model configuration as a ModelConfig object"""
        pass
    
    @abstractmethod
    def create_model_settings(self, **params) -> 'ModelSettings':
        """Create ModelSettings from configuration"""
        pass
    
    @abstractmethod
    def create_model_config(self, **params) -> 'ModelConfig':
        """Create and return a complete ModelConfig object"""
        pass