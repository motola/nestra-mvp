"""OAuth routes for device integrations."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from dependencies import OrganizationDep
from integrations.device_oauth.handler import get_device_oauth_handler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations/oauth", tags=["device_oauth"])


class AuthorizeRequest(BaseModel):
    """Request to get authorization URL."""

    vendor: str


class AuthorizeResponse(BaseModel):
    """Authorization URL response."""

    authorization_url: str


class CallbackRequest(BaseModel):
    """OAuth callback request."""

    vendor: str
    code: str
    state: str | None = None


class TokenResponse(BaseModel):
    """Token exchange response."""

    vendor: str
    access_token: str
    token_type: str
    expires_at: str | None = None


@router.post("/authorize", response_model=AuthorizeResponse)
async def authorize(
    request: AuthorizeRequest,
    org: OrganizationDep,
) -> AuthorizeResponse:
    """Get OAuth authorization URL for a vendor.

    Args:
        request: Vendor name
        org: Organization context

    Returns:
        Authorization URL to redirect user to
    """
    try:
        handler = get_device_oauth_handler()
        auth_url = handler.generate_authorization_url(request.vendor)
        return AuthorizeResponse(authorization_url=auth_url)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error("Failed to generate authorization URL: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authorization URL",
        ) from e


@router.post("/callback", response_model=TokenResponse)
async def handle_callback(
    request: CallbackRequest,
    org: OrganizationDep,
) -> TokenResponse:
    """Handle OAuth callback after user authorization.

    Args:
        request: Authorization code and vendor
        org: Organization context

    Returns:
        Token details

    Raises:
        HTTPException: If token exchange fails
    """
    if not request.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code",
        )

    try:
        handler = get_device_oauth_handler()

        # Exchange code for token
        token = await handler.exchange_code_for_token(request.vendor, request.code)

        # Store in database
        stored_token = await handler.store_token(org.id, request.vendor, token)

        return TokenResponse(
            vendor=stored_token.vendor,
            access_token=stored_token.access_token,
            token_type=stored_token.token_type,
            expires_at=stored_token.expires_at.isoformat() if stored_token.expires_at else None,
        )
    except ValueError as e:
        logger.warning("Token exchange failed for %s: %s", request.vendor, e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange authorization code for token",
        ) from e
    except Exception as e:
        logger.error("Callback handling failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process OAuth callback",
        ) from e


@router.get("/token/{vendor}")
async def get_token(
    vendor: str,
    org: OrganizationDep,
) -> TokenResponse:
    """Retrieve stored OAuth token for a vendor.

    Args:
        vendor: Vendor name
        org: Organization context

    Returns:
        Stored token or 404 if not found
    """
    try:
        handler = get_device_oauth_handler()
        token = await handler.get_token(org.id, vendor)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No OAuth token found for vendor: {vendor}",
            )

        return TokenResponse(
            vendor=token.vendor,
            access_token=token.access_token,
            token_type=token.token_type,
            expires_at=token.expires_at.isoformat() if token.expires_at else None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve token: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve token",
        ) from e


@router.delete("/token/{vendor}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    vendor: str,
    org: OrganizationDep,
) -> None:
    """Revoke OAuth token for a vendor.

    Args:
        vendor: Vendor name
        org: Organization context
    """
    # TODO: Implement token revocation (delete from DB)
    pass
