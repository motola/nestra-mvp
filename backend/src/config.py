from __future__ import annotations

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_SECRET = "dev-secret-key-change-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://localhost/alphacon"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = _INSECURE_SECRET
    debug: bool = False

    lifx_api_token: str = ""
    lifx_client_id: str = ""
    lifx_client_secret: str = ""
    govee_api_key: str = ""
    govee_ble_address: str = ""
    govee_client_id: str = ""
    govee_client_secret: str = ""
    meross_client_id: str = ""
    meross_client_secret: str = ""
    shelly_client_id: str = ""
    shelly_client_secret: str = ""
    anthropic_api_key: str = ""
    sendgrid_api_key: str = ""
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    microsoft_oauth_client_id: str = ""
    microsoft_oauth_client_secret: str = ""
    microsoft_oauth_tenant: str = "common"
    frontend_url: str = "https://nestra-mvp.fly.dev"
    backend_url: str = "https://nestra-mvp-api.fly.dev"

    @model_validator(mode="after")
    def _reject_insecure_secret_in_production(self) -> Settings:
        if not self.debug and self.secret_key == _INSECURE_SECRET:
            raise ValueError(
                "SECRET_KEY must be set to a secure value when debug=False. "
                "Set the SECRET_KEY environment variable."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
