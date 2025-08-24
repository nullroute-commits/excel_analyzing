"""Core configuration and settings management."""

from enum import Enum
from typing import Any, List

try:
    from pydantic import BaseSettings, Field, validator
except ImportError:
    from pydantic import Field, validator
    from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Application environment types."""

    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings with environment-specific configurations."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Application settings
    app_name: str = Field(default="Excel Analyzing", description="Application name")
    debug: bool = Field(default=False, description="Debug mode flag")
    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="Application environment"
    )

    # Database settings
    database_url: str = Field(
        default="postgresql://localhost/excel_analyzing", description="Database URL"
    )
    database_pool_size: int = Field(default=10, description="Database pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow")

    # Excel processing settings
    max_file_size_mb: int = Field(default=100, description="Max file size in MB")
    chunk_size: int = Field(default=1000, description="Processing chunk size")
    max_sheets_per_workbook: int = Field(
        default=50, description="Max sheets per workbook"
    )

    # Django settings
    django_secret_key: str = Field(
        default="dev-secret-key-change-in-production", description="Django secret key"
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"], description="Allowed hosts"
    )

    # Logging settings
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format",
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


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
