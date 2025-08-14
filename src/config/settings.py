import os
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, AnyUrl, Field
from typing import List, Optional, Union

# Get the project root directory (where .env should be located)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load environment variables from .env file in project root
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    print(f"Loading .env file from: {env_path}")
    load_dotenv(env_path)
else:
    # Fallback: try to load from current working directory
    print(f".env file not found at {env_path}, trying current directory")
    load_dotenv()

# Debug: Print some key environment variables to verify loading
print(f"ENV_NAME: {os.getenv('ENV_NAME', 'NOT_SET')}")
print(f"REDIS_URL: {os.getenv('REDIS_URL', 'NOT_SET')}")
print(f"SECRET_KEY: {'SET' if os.getenv('SECRET_KEY') else 'NOT_SET'}")
print(f"GEMINI_API_KEY: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT_SET'}")
print(f"TAVILY_API_KEY: {'SET' if os.getenv('TAVILY_API_KEY') else 'NOT_SET'}")


class Settings(BaseSettings):
    """Application settings with dynamic environment switching and security protocols."""
    
    # Let pydantic read env vars (we'll load the right file below)
    model_config = SettingsConfigDict(env_file=str(env_path) if env_path.exists() else ".env", case_sensitive=False, extra="allow")
    
    # ---- Core ----
    ENV_NAME: str = Field(default="development", env="ENV_NAME")  # development | staging | production
    
    # ---- Server ----
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    RELOAD: bool = Field(default=True, env="RELOAD")
    
    # ---- Redis ----
    REDIS_URL: AnyUrl = Field(default="redis://localhost:6379/0", env="REDIS_URL")  # supports redis://
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[SecretStr] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_USE_SSL: bool = Field(default=False, env="REDIS_USE_SSL")
    
    # ---- CORS ----
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="BACKEND_CORS_ORIGINS"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # ---- Security ----
    SECRET_KEY: SecretStr = Field(default="your-secret-key-here", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # ---- Rate Limiting ----
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # ---- Cache ----
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    CACHE_PREFIX: str = Field(default="deepsearch:", env="CACHE_PREFIX")
    
    # ---- External APIs ----
    OPENAI_API_KEY: Optional[SecretStr] = Field(default=None, env="OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[SecretStr] = Field(default=None, env="GEMINI_API_KEY")
    TAVILY_API_KEY: Optional[SecretStr] = Field(default=None, env="TAVILY_API_KEY")
    
    # ---- Example secret / external ----
    API_KEY: SecretStr = Field(default="default-api-key", env="API_KEY")
    
    @property
    def is_development(self) -> bool:
        """Check if current environment is development."""
        return self.ENV_NAME == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if current environment is production."""
        return self.ENV_NAME == "production"
    
    @property
    def is_staging(self) -> bool:
        """Check if current environment is staging."""
        return self.ENV_NAME == "staging"
    
    @property
    def cors_config(self) -> dict:
        """Get CORS configuration dictionary."""
        return {
            "allow_origins": self.BACKEND_CORS_ORIGINS,
            "allow_credentials": self.CORS_ALLOW_CREDENTIALS,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["*"],
            "expose_headers": ["Content-Length", "X-Total-Count"],
        }


@lru_cache
def load_config():
    """Load configuration with caching."""
    return Settings()


# Export settings instance
settings = load_config()

# Debug: Show the difference between os.getenv and Pydantic settings
print("\n--- Pydantic Settings Values ---")
print(f"settings.ENV_NAME: {settings.ENV_NAME}")
print(f"settings.REDIS_URL: {settings.REDIS_URL}")
print(f"settings.GEMINI_API_KEY: {'SET' if settings.GEMINI_API_KEY else 'NOT_SET'}")
print(f"settings.TAVILY_API_KEY: {'SET' if settings.TAVILY_API_KEY else 'NOT_SET'}")