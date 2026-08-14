from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config import get_settings
from db import SessionLocal
from dependencies import SettingsDep
from identity.api.schemas import (
    LoginRequest,
    MeResponse,
    OrganizationOut,
    SignupRequest,
    TokenResponse,
    UserOut,
)
from identity.domain.roles import AuthMethod, OrgRole, OrgStatus, SubscriptionTier
from identity.repository.models import (
    OrganizationModel,
    OrgMembershipModel,
    PortfolioModel,
    UserModel,
)
from identity.services.signup import _hash_password, _verify_password

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


def _decode_token(token: str, secret_key: str) -> dict[str, Any]:
    """Decode and verify a JWT token."""
    try:
        return jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup_endpoint(
    body: SignupRequest,
    settings: SettingsDep,
) -> TokenResponse:
    """Create a new user, organization, default portfolio, and membership."""
    now = datetime.now(tz=UTC)
    slug = body.org_name.lower().replace(" ", "-")

    async with SessionLocal() as session:
        # Check if email already exists
        result = await session.execute(select(UserModel).where(UserModel.email == body.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )

        try:
            # Create organization
            org = OrganizationModel(
                name=body.org_name,
                slug=slug,
                legal_name=body.legal_name,
                status=OrgStatus.ACTIVE,
                subscription_tier=SubscriptionTier.STARTER,
                created_at=now,
            )
            session.add(org)
            await session.flush()

            # Create user
            user = UserModel(
                email=body.email,
                full_name=body.full_name,
                password_hash=_hash_password(body.password),
                auth_method=AuthMethod.PASSWORD,
                is_active=True,
            )
            session.add(user)
            await session.flush()

            # Create default portfolio
            portfolio = PortfolioModel(
                organization_id=org.id,
                name="Default Portfolio",
                description="",
                is_default=True,
                created_at=now,
            )
            session.add(portfolio)

            # Create org membership
            membership = OrgMembershipModel(
                user_id=user.id,
                organization_id=org.id,
                org_role=OrgRole.OWNER,
                joined_at=now,
            )
            session.add(membership)

            await session.commit()

            token = _create_token(user.id, org.id, settings.secret_key)
            return TokenResponse(
                access_token=token,
                token_type="bearer",
                organization_id=org.id,
            )
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email or organization slug already in use",
            ) from e


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(
    body: LoginRequest,
    settings: SettingsDep,
) -> TokenResponse:
    """Authenticate with email + password and return a JWT."""
    async with SessionLocal() as session:
        # Query user by email
        result = await session.execute(select(UserModel).where(UserModel.email == body.email))
        user = result.scalar_one_or_none()

        if not user or not _verify_password(body.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Get user's first organization (default to first membership)
        membership_result = await session.execute(
            select(OrgMembershipModel).where(OrgMembershipModel.user_id == user.id)
        )
        membership = membership_result.scalars().first()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User has no organization membership",
            )

        token = _create_token(user.id, membership.organization_id, settings.secret_key)
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
async def me_endpoint(auth: str | None = None) -> MeResponse:
    """Return the authenticated user and their active organization.

    For now, accepts ?auth=<token> query param for testing.
    TODO: Replace with proper Authorization header middleware.
    """
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
        )

    settings = get_settings()
    payload = _decode_token(auth, settings.secret_key)

    user_id = UUID(payload["sub"])
    org_id = UUID(payload["org"])

    async with SessionLocal() as session:
        # Query user from database
        user_result = await session.execute(select(UserModel).where(UserModel.id == user_id))
        user = user_result.scalar_one_or_none()

        # Query organization from database
        org_result = await session.execute(
            select(OrganizationModel).where(OrganizationModel.id == org_id)
        )
        org = org_result.scalar_one_or_none()

        if not user or not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User or organization not found",
            )

        return MeResponse(
            user=UserOut(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
            ),
            organization=OrganizationOut(
                id=org.id,
                name=org.name,
                slug=org.slug,
            ),
        )
