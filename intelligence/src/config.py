"""Intelligence service configuration."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # App
    debug: bool = Field(default=False, description="Enable debug mode")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/alphacon_dev",
        description="PostgreSQL connection URL",
    )

    # Anthropic
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key for Claude access",
    )

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
