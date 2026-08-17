"""Generic OAuth 2.0 handler for device integrations."""

from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

import httpx

from config import get_settings
from db import SessionLocal
from integrations.device_oauth.config import get_oauth_config
from integrations.device_oauth.models import OAuthTokenModel, OAuthTokenOut

logger = logging.getLogger(__name__)


class DeviceOAuthHandler:
    """Handles OAuth 2.0 authorization code flow for device vendors."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_authorization_url(
        self,
        vendor: str,
        state: str | None = None,
    ) -> str:
        """Generate OAuth authorization URL for the vendor.

        Args:
            vendor: Vendor name (e.g., "lifx", "shelly_cloud")
            state: Optional state parameter for CSRF protection

        Returns:
            Full authorization URL
        """
        config = get_oauth_config(vendor)
        state = state or secrets.token_urlsafe(32)

        params = {
            "client_id": config.client_id,
            "redirect_uri": f"{self.settings.backend_url}{config.redirect_uri_path}",
            "response_type": "code",
            "scope": " ".join(config.scopes),
            "state": state,
        }

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{config.auth_url}?{query_string}"

    async def exchange_code_for_token(
        self,
        vendor: str,
        code: str,
    ) -> OAuthTokenOut:
        """Exchange authorization code for access token.

        Args:
            vendor: Vendor name
            code: Authorization code from OAuth callback

        Returns:
            OAuthTokenOut with access token details

        Raises:
            ValueError: If token exchange fails
        """
        config = get_oauth_config(vendor)

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "redirect_uri": f"{self.settings.backend_url}{config.redirect_uri_path}",
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(config.token_url, data=payload)
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            logger.error("Token exchange failed for %s: %s", vendor, e)
            raise ValueError(f"Failed to exchange code for token: {e}") from e

        # Parse response (varies by vendor)
        access_token = data.get("access_token")
        token_type = data.get("token_type", "Bearer")
        refresh_token = data.get("refresh_token")
        expires_in = data.get("expires_in")

        expires_at = None
        if expires_in:
            expires_at = datetime.now(tz=UTC) + timedelta(seconds=expires_in)

        return OAuthTokenOut(
            id=UUID(int=0),  # Placeholder, will be set in DB
            organization_id=UUID(int=0),  # Set by caller
            vendor=vendor,
            access_token=access_token,
            token_type=token_type,
            refresh_token=refresh_token,
            expires_at=expires_at,
            created_at=datetime.now(tz=UTC),
            updated_at=datetime.now(tz=UTC),
        )

    async def store_token(
        self,
        organization_id: UUID,
        vendor: str,
        token: OAuthTokenOut,
    ) -> OAuthTokenOut:
        """Store OAuth token in database.

        Args:
            organization_id: Organization ID
            vendor: Vendor name
            token: Token data to store

        Returns:
            Stored token with generated ID
        """
        now = datetime.now(tz=UTC)

        async with SessionLocal() as session:
            # Check if token already exists for this org+vendor
            existing = (
                await session.query(OAuthTokenModel)
                .filter_by(
                    organization_id=organization_id,
                    vendor=vendor,
                )
                .first()
            )

            if existing:
                # Update existing token
                existing.access_token = token.access_token
                existing.token_type = token.token_type
                existing.refresh_token = token.refresh_token
                existing.expires_at = token.expires_at
                existing.updated_at = now
                session.add(existing)
            else:
                # Create new token
                db_token = OAuthTokenModel(
                    organization_id=organization_id,
                    vendor=vendor,
                    access_token=token.access_token,
                    token_type=token.token_type,
                    refresh_token=token.refresh_token,
                    expires_at=token.expires_at,
                    created_at=now,
                    updated_at=now,
                )
                session.add(db_token)

            await session.commit()

            # Reload to get ID
            if existing:
                await session.refresh(existing)
                return OAuthTokenOut.from_orm(existing)
            else:
                await session.refresh(db_token)
                return OAuthTokenOut.from_orm(db_token)

    async def get_token(
        self,
        organization_id: UUID,
        vendor: str,
    ) -> OAuthTokenOut | None:
        """Retrieve stored OAuth token.

        Args:
            organization_id: Organization ID
            vendor: Vendor name

        Returns:
            Stored token or None if not found
        """
        async with SessionLocal() as session:
            token = (
                await session.query(OAuthTokenModel)
                .filter_by(
                    organization_id=organization_id,
                    vendor=vendor,
                )
                .first()
            )

            if token:
                return OAuthTokenOut.from_orm(token)
            return None

    async def is_token_expired(
        self,
        organization_id: UUID,
        vendor: str,
    ) -> bool:
        """Check if stored token is expired.

        Args:
            organization_id: Organization ID
            vendor: Vendor name

        Returns:
            True if token is expired or not found
        """
        token = await self.get_token(organization_id, vendor)
        if not token or not token.expires_at:
            return False

        return datetime.now(tz=UTC) >= token.expires_at


def get_device_oauth_handler() -> DeviceOAuthHandler:
    """Dependency injection for DeviceOAuthHandler."""
    return DeviceOAuthHandler()
