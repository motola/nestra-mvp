from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://localhost/alphacon"
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = False

    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""

    # Demo mode
    demo_mode: bool = False

    # CORS — comma-separated allowed origins. Set this to point the API at any
    # frontend; the backend is frontend-agnostic.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # Vendor integrations
    govee_api_key: str = ""
    lifx_api_token: str = ""
    shelly_auth_key: str = ""
    hue_api_key: str = ""
    smartthings_token: str = ""
    tuya_access_id: str = ""
    tuya_access_secret: str = ""
    switchbot_token: str = ""
    switchbot_secret: str = ""
    ecobee_access_token: str = ""
    tado_access_token: str = ""
    kasa_token: str = ""
    august_access_token: str = ""
    august_api_key: str = ""  # August's public app key (see py-august / Home Assistant)
    aqara_access_token: str = ""
    ewelink_access_token: str = ""

    # AI
    anthropic_api_key: str = ""

    # Upstash Redis REST API
    upstash_redis_rest_url: str = ""
    upstash_redis_rest_token: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
