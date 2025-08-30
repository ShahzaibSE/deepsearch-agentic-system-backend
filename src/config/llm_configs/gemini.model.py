from dotenv import load_dotenv
import os
from agents import AsyncOpenAI, ModelSettings
from base_model import BaseModelConfig, ModelConfig
from typing import Dict, Any


class GeminiConfig(BaseModelConfig):
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        super().__init__(api_key)
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = "gemini-pro"
    
    def get_client(self):
        """Get the configured Gemini client"""
        return self.client
    
    def create_model_settings(self, **params) -> ModelSettings:
        """Create ModelSettings from configuration"""
        # Default Gemini settings
        default_settings = {
            "model": self.model_name,
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        # Override with any passed parameters
        default_settings.update(params)
        
        # Create ModelSettings object
        return ModelSettings(**default_settings)
    
    def get_model_config(self, **params) -> ModelConfig:
        """Get the complete model configuration as a ModelConfig object"""
        # Create ModelSettings first
        model_settings = self.create_model_settings(**params)
        
        # Return complete ModelConfig object
        return ModelConfig(
            model_name=self.model_name,
            model_settings=model_settings,
            client=self.get_client(),
            api_key=self.api_key
        )
    
    def create_model_config(self, **params) -> ModelConfig:
        """Create and return a complete ModelConfig object"""
        return self.get_model_config(**params)