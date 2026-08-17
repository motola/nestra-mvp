from __future__ import annotations

import asyncio
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import httpx
import jwt
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config import get_settings
from db import SessionLocal
from dependencies import SettingsDep
from identity.api.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    GoogleOAuthCallbackRequest,
    GoogleOAuthUrlResponse,
    LoginRequest,
    MeResponse,
    OrganizationOut,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
    UserOut,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from identity.domain.roles import AuthMethod, OrgRole, OrgStatus, SubscriptionTier
from identity.repository.models import (
    OrganizationModel,
    OrgMembershipModel,
    PortfolioModel,
    TokenType,
    UserModel,
    VerificationTokenModel,
)
from identity.services.email_service import get_email_service
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

            # Create email verification token
            verify_token = secrets.token_urlsafe(32)
            verify_expires = now + timedelta(hours=24)
            verification_token = VerificationTokenModel(
                user_id=user.id,
                token=verify_token,
                token_type=TokenType.EMAIL_VERIFICATION,
                expires_at=verify_expires,
                created_at=now,
            )
            session.add(verification_token)

            await session.commit()

            # Send welcome and verification emails asynchronously (don't wait for completion)
            email_service = get_email_service()
            asyncio.create_task(email_service.send_welcome_email(user.email, user.full_name))
            asyncio.create_task(
                email_service.send_verification_email(user.email, user.full_name, verify_token)
            )

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

        if (
            not user
            or not user.password_hash
            or not _verify_password(body.password, user.password_hash)
        ):
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


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password_endpoint(body: ForgotPasswordRequest) -> ForgotPasswordResponse:
    """Generate a password reset token and send it to the user's email.

    Returns a success message without revealing if the email exists.
    """
    now = datetime.now(tz=UTC)
    expires = now + timedelta(hours=24)

    async with SessionLocal() as session:
        # Query user by email
        result = await session.execute(select(UserModel).where(UserModel.email == body.email))
        user = result.scalar_one_or_none()

        # Generate token regardless of user existence (security best practice)
        token = secrets.token_urlsafe(32)

        if user:
            try:
                # Create verification token in database
                verification_token = VerificationTokenModel(
                    user_id=user.id,
                    token=token,
                    token_type=TokenType.PASSWORD_RESET,
                    expires_at=expires,
                    created_at=now,
                )
                session.add(verification_token)
                await session.commit()

                # Send reset email asynchronously (don't wait for completion)
                email_service = get_email_service()
                asyncio.create_task(
                    email_service.send_password_reset_email(
                        user.email,
                        user.full_name,
                        token,
                    )
                )

            except IntegrityError as e:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create reset token",
                ) from e

        return ForgotPasswordResponse(message="Check your email for password reset instructions")


@router.post("/reset-password", response_model=TokenResponse)
async def reset_password_endpoint(
    body: ResetPasswordRequest,
    settings: SettingsDep,
) -> TokenResponse:
    """Reset a user's password using a valid reset token.

    Returns a new JWT token for immediate login after password reset.
    """
    async with SessionLocal() as session:
        # Query verification token
        result = await session.execute(
            select(VerificationTokenModel).where(VerificationTokenModel.token == body.token)
        )
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

        now = datetime.now(tz=UTC)

        # Check if token is expired
        if token_record.expires_at < now:
            # Clean up expired token
            await session.delete(token_record)
            await session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has expired",
            )

        # Check if token has already been used
        if token_record.used_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has already been used",
            )

        # Verify token type
        if token_record.token_type != TokenType.PASSWORD_RESET:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type",
            )

        # Query user
        user_result = await session.execute(
            select(UserModel).where(UserModel.id == token_record.user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        try:
            # Update user password
            user.password_hash = _hash_password(body.new_password)

            # Mark token as used
            token_record.used_at = now

            await session.commit()

            # Get user's first organization for token creation
            membership_result = await session.execute(
                select(OrgMembershipModel).where(OrgMembershipModel.user_id == user.id)
            )
            membership = membership_result.scalars().first()

            if not membership:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="User has no organization membership",
                )

            # Send password reset confirmation email asynchronously
            email_service = get_email_service()
            asyncio.create_task(
                email_service.send_password_reset_confirmation_email(user.email, user.full_name)
            )

            # Create and return JWT token
            jwt_token = _create_token(user.id, membership.organization_id, settings.secret_key)
            return TokenResponse(
                access_token=jwt_token,
                token_type="bearer",
                organization_id=membership.organization_id,
            )

        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password",
            ) from e


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email_endpoint(body: VerifyEmailRequest) -> VerifyEmailResponse:
    """Verify a user's email address using a verification token."""
    async with SessionLocal() as session:
        # Query verification token
        result = await session.execute(
            select(VerificationTokenModel).where(VerificationTokenModel.token == body.token)
        )
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

        now = datetime.now(tz=UTC)

        # Check if token is expired
        if token_record.expires_at < now:
            # Clean up expired token
            await session.delete(token_record)
            await session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has expired",
            )

        # Check if token has already been used
        if token_record.used_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email has already been verified",
            )

        # Verify token type
        if token_record.token_type != TokenType.EMAIL_VERIFICATION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type",
            )

        # Query user
        user_result = await session.execute(
            select(UserModel).where(UserModel.id == token_record.user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        try:
            # Mark email as verified
            user.email_verified = True

            # Mark token as used
            token_record.used_at = now

            await session.commit()

            return VerifyEmailResponse(message="Email verified successfully")

        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify email",
            ) from e


@router.post("/resend-verification-email", status_code=status.HTTP_204_NO_CONTENT)
async def resend_verification_email_endpoint(
    body: VerifyEmailRequest,
) -> None:
    """Resend verification email to user's email address."""
    async with SessionLocal() as session:
        # Find user by their pending verification token
        result = await session.execute(
            select(VerificationTokenModel).where(VerificationTokenModel.token == body.token)
        )
        token_record = result.scalar_one_or_none()

        if not token_record:
            # Token doesn't exist - silently succeed (privacy)
            return

        # Query user
        user_result = await session.execute(
            select(UserModel).where(UserModel.id == token_record.user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            return

        # Send verification email asynchronously
        email_service = get_email_service()
        asyncio.create_task(
            email_service.send_verification_email(user.email, user.full_name, token_record.token)
        )


@router.get("/google/url", response_model=GoogleOAuthUrlResponse)
async def google_oauth_url_endpoint(settings: SettingsDep) -> GoogleOAuthUrlResponse:
    """Generate and return the Google OAuth authorization URL.

    Requires Google OAuth credentials to be set via fly secrets:
      flyctl secrets set GOOGLE_OAUTH_CLIENT_ID=<client_id>
      flyctl secrets set GOOGLE_OAUTH_CLIENT_SECRET=<client_secret>
    """
    if not settings.google_oauth_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured",
        )

    params = {
        "client_id": settings.google_oauth_client_id,
        "redirect_uri": f"{settings.frontend_url}/auth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return GoogleOAuthUrlResponse(url=url)


@router.post("/google/callback", response_model=TokenResponse)
async def google_oauth_callback_endpoint(
    body: GoogleOAuthCallbackRequest,
    settings: SettingsDep,
) -> TokenResponse:
    """Exchange Google authorization code for user token."""
    if not settings.google_oauth_client_id or not settings.google_oauth_client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured",
        )

    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": body.code,
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "redirect_uri": f"{settings.frontend_url}/auth/google/callback",
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to exchange authorization code",
            )

        token_data = token_response.json()

        # Verify ID token and get user info
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to get user info from Google",
            )

        user_info = user_response.json()
        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name", "Google User")

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required info from Google",
        )

    now = datetime.now(tz=UTC)

    async with SessionLocal() as session:
        # Try to find user by google_id first
        result = await session.execute(select(UserModel).where(UserModel.google_id == google_id))
        user = result.scalar_one_or_none()

        if user:
            # Existing Google OAuth user
            user.last_login_at = now
            await session.commit()
        else:
            # Check if user exists by email
            email_result = await session.execute(select(UserModel).where(UserModel.email == email))
            email_user = email_result.scalar_one_or_none()

            if email_user:
                # Link Google ID to existing user
                email_user.google_id = google_id
                email_user.auth_method = AuthMethod.GOOGLE_SSO
                email_user.last_login_at = now
                email_user.email_verified = True
                user = email_user
                await session.commit()
            else:
                # Create new user with Google OAuth
                try:
                    # Create organization for new user
                    slug = email.split("@")[0].lower()
                    org = OrganizationModel(
                        name=f"{name}'s Portfolio",
                        slug=slug,
                        legal_name=name,
                        status=OrgStatus.ACTIVE,
                        subscription_tier=SubscriptionTier.STARTER,
                        created_at=now,
                    )
                    session.add(org)
                    await session.flush()

                    # Create user
                    user = UserModel(
                        email=email,
                        full_name=name,
                        google_id=google_id,
                        password_hash=None,
                        auth_method=AuthMethod.GOOGLE_SSO,
                        is_active=True,
                        email_verified=True,
                        last_login_at=now,
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
                except IntegrityError as e:
                    await session.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Failed to create user account",
                    ) from e

        # Get user's first organization
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
