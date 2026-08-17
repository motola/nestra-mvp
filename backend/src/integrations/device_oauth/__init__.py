"""Device OAuth integration — shared OAuth 2.0 handler for all vendors."""

from integrations.device_oauth.config import get_oauth_config
from integrations.device_oauth.handler import DeviceOAuthHandler, get_device_oauth_handler
from integrations.device_oauth.models import OAuthConfig, OAuthTokenModel, OAuthTokenOut
from integrations.device_oauth.routes import router

__all__ = [
    "OAuthConfig",
    "OAuthTokenModel",
    "OAuthTokenOut",
    "DeviceOAuthHandler",
    "get_device_oauth_handler",
    "get_oauth_config",
    "router",
]
