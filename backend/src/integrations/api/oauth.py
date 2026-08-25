"""OAuth callback handlers for vendor integrations."""

from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

from config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["oauth"])

settings = get_settings()


@router.get("/{vendor}/callback")
async def oauth_callback(
    vendor: str,
    code: str = Query(...),
    state: str | None = Query(None),
) -> dict[str, Any]:
    """Handle OAuth callback from vendor and exchange code for token."""
    vendor = vendor.lower()

    try:
        if vendor == "lifx":
            return await _handle_lifx_callback(code)
        elif vendor == "govee":
            return await _handle_govee_callback(code)
        elif vendor == "meross":
            return await _handle_meross_callback(code)
        elif vendor == "shelly":
            return await _handle_shelly_callback(code)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown vendor: {vendor}")
    except Exception as e:
        logger.error(f"OAuth callback failed for {vendor}: {e}")
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}") from e


async def _handle_lifx_callback(code: str) -> dict[str, Any]:
    """Exchange LIFX authorization code for access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.lifx.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.lifx_client_id,
                "client_secret": settings.lifx_client_secret,
            },
        )
        response.raise_for_status()
        data = response.json()

        return {
            "vendor": "lifx",
            "access_token": data.get("access_token"),
            "token_type": data.get("token_type", "Bearer"),
            "expires_in": data.get("expires_in"),
        }


async def _handle_govee_callback(code: str) -> dict[str, Any]:
    """Exchange Govee authorization code for access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.govee.com/oauth/token",
            json={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.govee_client_id,
                "client_secret": settings.govee_client_secret,
                "redirect_uri": f"{settings.frontend_url}/auth/govee/callback",
            },
        )
        response.raise_for_status()
        data = response.json()

        return {
            "vendor": "govee",
            "access_token": data.get("access_token"),
            "token_type": data.get("token_type", "Bearer"),
            "expires_in": data.get("expires_in"),
        }


async def _handle_meross_callback(code: str) -> dict[str, Any]:
    """Exchange Meross authorization code for access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://iot.meross.com/oauth/token",
            json={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.meross_client_id,
                "client_secret": settings.meross_client_secret,
                "redirect_uri": f"{settings.frontend_url}/auth/meross/callback",
            },
        )
        response.raise_for_status()
        data = response.json()

        return {
            "vendor": "meross",
            "access_token": data.get("access_token"),
            "token_type": data.get("token_type", "Bearer"),
            "expires_in": data.get("expires_in"),
        }


async def _handle_shelly_callback(code: str) -> dict[str, Any]:
    """Exchange Shelly authorization code for access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://auth.shelly.cloud/oauth/token",
            json={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.shelly_client_id,
                "client_secret": settings.shelly_client_secret,
                "redirect_uri": f"{settings.frontend_url}/auth/shelly/callback",
            },
        )
        response.raise_for_status()
        data = response.json()

        return {
            "vendor": "shelly",
            "access_token": data.get("access_token"),
            "token_type": data.get("token_type", "Bearer"),
            "expires_in": data.get("expires_in"),
        }
