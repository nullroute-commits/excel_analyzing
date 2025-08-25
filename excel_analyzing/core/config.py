"""Core configuration and settings management."""

import os
from enum import Enum
from pathlib import Path
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


class Settings(BaseSettings):  # type: ignore
    """Application settings with environment-specific configurations."""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_parse_none_str": "None",
        "use_enum_values": True,
    }

    # Application settings
    app_name: str = Field(default="Excel Analyzing", description="Application name")
    debug: bool = Field(default=False, description="Debug mode flag")
    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="Application environment"
    )

    # Database settings (hostname-based)
    database_host: str = Field(default="db-service", description="Database hostname")
    database_port: int = Field(default=5432, description="Database port")
    database_name: str = Field(default="excel_analyzing", description="Database name")
    database_user: str = Field(default="postgres", description="Database user")
    database_password: str = Field(default="password", description="Database password")
    database_pool_size: int = Field(default=10, description="Database pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow")

    # Cache settings (hostname-based)
    redis_host: str = Field(default="cache-service", description="Redis hostname")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database")
    redis_password: str = Field(default="", description="Redis password")

    # Excel processing settings
    max_file_size_mb: int = Field(default=100, description="Max file size in MB")
    chunk_size: int = Field(default=1000, description="Processing chunk size")
    max_sheets_per_workbook: int = Field(
        default=50, description="Max sheets per workbook"
    )
    processing_timeout: int = Field(
        default=300, description="Processing timeout in seconds"
    )
    max_concurrent_jobs: int = Field(
        default=4, description="Max concurrent processing jobs"
    )

    # Django settings
    django_secret_key: str = Field(
        default=(
            "dev-secret-key-change-in-production-this-is-long-enough-for-"
            "security-tests"
        ),
        description="Django secret key",
    )
    allowed_hosts: List[str] = Field(
        default=["web-service", "localhost", "127.0.0.1"], description="Allowed hosts"
    )

    # URL settings (hostname-based)
    api_base_url: str = Field(
        default="http://web-service:8000/api", description="API base URL"
    )
    frontend_url: str = Field(
        default="http://web-service:8000", description="Frontend URL"
    )

    # Logging settings
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format",
    )

    @property
    def database_url(self) -> str:
        """Construct database URL from hostname-based components."""
        return (
            f"postgresql://{self.database_user}:{self.database_password}@"
            f"{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def redis_url(self) -> str:
        """Construct Redis URL from hostname-based components."""
        if self.redis_password:
            return (
                f"redis://:{self.redis_password}@{self.redis_host}:"
                f"{self.redis_port}/{self.redis_db}"
            )
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v: Any) -> List[str]:
        """Parse comma-separated allowed hosts."""
        if isinstance(v, str):
            # Handle comma-separated values from environment variables
            return [host.strip() for host in v.split(",") if host.strip()]
        elif isinstance(v, list):
            return v
        return v

    @validator("environment", pre=True)
    def validate_environment(cls, v: Any) -> Environment:
        """Validate and convert environment string to enum."""
        if isinstance(v, str):
            return Environment(v.lower())
        return v


def get_settings() -> Settings:
    """Get application settings instance with environment-specific configuration."""
    # Get current environment
    env = os.getenv("ENVIRONMENT", "development")

    # Define base path for environment configurations
    base_path = Path(__file__).parent.parent.parent / "env"

    # Clear any previously loaded environment variables that might conflict
    env_vars_to_clear = [
        "DJANGO_ALLOWED_HOSTS",
        "DJANGO_SECRET_KEY",
        "DJANGO_DEBUG",
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_NAME",
        "DATABASE_USER",
        "DATABASE_PASSWORD",
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_DB",
        "REDIS_PASSWORD",
        "API_BASE_URL",
        "FRONTEND_URL",
    ]
    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]

    # Load configuration files based on service and environment
    env_files = [
        base_path / "web" / "django" / f".env.{env}",
        base_path / "database" / "postgresql" / f".env.{env}",
        base_path / "cache" / "redis" / f".env.{env}",
        base_path / "processing" / "core" / f".env.{env}",
    ]

    # Add root .env file if it exists
    root_env = base_path.parent / ".env"
    if root_env.exists():
        env_files.append(root_env)

    # Filter existing files and convert to strings
    existing_env_files = [str(f) for f in env_files if f.exists()]

    # Load environment variables from files
    # Environment files are loaded in the following order:
    #   1. web/django/.env.{env}
    #   2. database/postgresql/.env.{env}
    #   3. cache/redis/.env.{env}
    #   4. processing/core/.env.{env}
    #   5. root .env (if exists)
    # Because override=True is used, variables from later files will override
    # those from earlier files.
    # This makes the last file in the list highest precedence.
    for env_file in existing_env_files:
        from dotenv import load_dotenv

        load_dotenv(env_file, override=True)

    # Create settings instance
    settings = Settings()

    # Set environment
    settings.environment = Environment(env)
    # Set environment variable before creating settings instance
    os.environ["ENVIRONMENT"] = env
    settings = Settings()
    # Post-process environment-specific overrides
    django_allowed_hosts = os.getenv("DJANGO_ALLOWED_HOSTS")
    if django_allowed_hosts:
        settings.allowed_hosts = [
            host.strip() for host in django_allowed_hosts.split(",") if host.strip()
        ]

    django_secret_key = os.getenv("DJANGO_SECRET_KEY")
    if django_secret_key:
        settings.django_secret_key = django_secret_key

    django_debug = os.getenv("DJANGO_DEBUG")
    if django_debug:
        settings.debug = django_debug.lower() in ("true", "1", "yes", "on")

    return settings


# Global settings instance - will be initialized once at import time
settings = get_settings()


def get_default_settings() -> dict:
    """Get default settings as a dictionary for regression testing."""
    default_settings = Settings()
    return {
        "app_name": default_settings.app_name,
        "debug": default_settings.debug,
        "environment": default_settings.environment,
        "database_host": default_settings.database_host,
        "database_port": default_settings.database_port,
        "database_name": default_settings.database_name,
        "max_file_size_mb": default_settings.max_file_size_mb,
        "chunk_size": default_settings.chunk_size,
        "max_sheets_per_workbook": default_settings.max_sheets_per_workbook,
        "processing_timeout": default_settings.processing_timeout,
        "max_concurrent_jobs": default_settings.max_concurrent_jobs,
        "log_level": default_settings.log_level,
        "allowed_hosts": default_settings.allowed_hosts,
    }
