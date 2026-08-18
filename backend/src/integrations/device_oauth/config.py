"""OAuth configuration registry for device vendors."""

from __future__ import annotations

from config import get_settings
from integrations.device_oauth.models import OAuthConfig


def create_oauth_config(vendor: str) -> OAuthConfig:
    """Factory to create OAuthConfig for a vendor.

    Raises ValueError if vendor not configured.
    """
    settings = get_settings()

    configs: dict[str, OAuthConfig] = {
        "lifx": OAuthConfig(
            vendor="lifx",
            client_id=settings.lifx_client_id,
            client_secret=settings.lifx_client_secret,
            auth_url="https://api.lifx.com/oauth/authorize",
            token_url="https://api.lifx.com/oauth/token",
            scopes=["remote_control:all"],
            redirect_uri_path="/integrations/oauth/callback/lifx",
        ),
        "shelly_cloud": OAuthConfig(
            vendor="shelly_cloud",
            client_id=settings.shelly_client_id,
            client_secret=settings.shelly_client_secret,
            auth_url="https://app.shelly.cloud/oauth/authorize",
            token_url="https://app.shelly.cloud/oauth/token",
            scopes=["user:read", "device:read"],
            redirect_uri_path="/integrations/oauth/callback/shelly_cloud",
        ),
    }

    if vendor not in configs:
        raise ValueError(f"OAuth not configured for vendor: {vendor}")

    return configs[vendor]


def get_oauth_config(vendor: str) -> OAuthConfig:
    """Get OAuth config for a vendor, with error handling."""
    try:
        return create_oauth_config(vendor)
    except ValueError as e:
        raise ValueError(f"OAuth config error: {e}") from e
