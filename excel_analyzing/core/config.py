"""Core configuration and settings management."""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pydantic import BaseSettings, Field, validator
except ImportError:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator


class Environment(str, Enum):
    """Application environment types."""
    
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings with environment-specific configurations."""
    
    # Application settings
    app_name: str = Field(default="Excel Analyzing", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    
    # Database settings
    database_url: str = Field(
        default="postgresql://localhost/excel_analyzing",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Excel processing settings
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    max_sheets_per_workbook: int = Field(default=50, env="MAX_SHEETS_PER_WORKBOOK")
    
    # Django settings
    django_secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        env="DJANGO_SECRET_KEY"
    )
    allowed_hosts: List[str] = Field(default=["localhost", "127.0.0.1"], env="ALLOWED_HOSTS")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v: Any) -> List[str]:
        """Parse comma-separated allowed hosts."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("environment", pre=True)
    def validate_environment(cls, v: Any) -> Environment:
        """Validate and convert environment string to enum."""
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    class Config:
        """Pydantic configuration."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()