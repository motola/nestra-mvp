from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://localhost/alphacon"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = False

    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""

    # Demo mode
    demo_mode: bool = False

    # Vendor integrations
    govee_api_key: str = ""
    lifx_api_token: str = ""
    shelly_auth_key: str = ""

    # AI
    anthropic_api_key: str = ""

    # Upstash Redis (optional, for background workers)
    upstash_redis_url: str = ""
    upstash_redis_token: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
