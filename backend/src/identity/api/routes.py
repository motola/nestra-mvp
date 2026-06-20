from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from dependencies import SettingsDep
from identity.api.schemas import (
    LoginRequest,
    MeResponse,
    SignupRequest,
    TokenResponse,
)
from identity.repository.models import OrgMembershipModel, UserModel
from identity.services.signup import _verify_password
from identity.services.signup import signup as signup_service
from shared.db import SessionLocal

router = APIRouter(prefix="/auth", tags=["identity"])


def _create_token(user_id: UUID, org_id: UUID, secret_key: str) -> str:
    """Create a JWT token valid for 7 days."""
    now = datetime.now(tz=UTC)
    expires = now + timedelta(days=7)
    payload = {
        "sub": str(user_id),
        "org": str(org_id),
        "iat": now.timestamp(),
        "exp": expires.timestamp(),
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup_endpoint(
    body: SignupRequest,
    settings: SettingsDep,
) -> TokenResponse:
    """Create a new user, organization, default portfolio, and membership."""
    async with SessionLocal() as session:
        # Check if user exists
        result = await session.execute(select(UserModel).where(UserModel.email == body.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )

        signup_result = await signup_service(
            session,
            email=body.email,
            full_name=body.full_name,
            password=body.password,
            org_name=body.org_name,
            legal_name=body.legal_name,
        )
        await session.commit()

    token = _create_token(signup_result.user.id, signup_result.organization.id, settings.secret_key)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        organization_id=signup_result.organization.id,
    )


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(
    body: LoginRequest,
    settings: SettingsDep,
) -> TokenResponse:
    """Authenticate with email + password and return a JWT."""
    async with SessionLocal() as session:
        result = await session.execute(select(UserModel).where(UserModel.email == body.email))
        user_row = result.scalar_one_or_none()
        if not user_row or not _verify_password(body.password, user_row.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Find user's organization (via membership)
        membership_result = await session.execute(
            select(OrgMembershipModel).where(OrgMembershipModel.user_id == user_row.id)
        )
        membership = membership_result.scalar_one_or_none()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User has no organization membership",
            )

        token = _create_token(user_row.id, membership.organization_id, settings.secret_key)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            organization_id=membership.organization_id,
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_endpoint() -> None:
    """Revoke the current session token (stateless — just return 204)."""
    pass


@router.get("/me", response_model=MeResponse)
async def me_endpoint() -> MeResponse:
    """Return the authenticated user and their active organization."""
    # TODO: Extract user_id and org_id from JWT in Authorization header
    # For now, return 501 until JWT middleware is wired
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="JWT middleware not yet wired",
    )
