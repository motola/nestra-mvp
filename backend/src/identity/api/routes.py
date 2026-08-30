from __future__ import annotations

import asyncio
import logging
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import httpx
import jwt
from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config import get_settings
from db import SessionLocal
from dependencies import SettingsDep
from identity.api.schemas import (
    EmailAvailabilityRequest,
    EmailAvailabilityResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    GoogleOAuthCallbackRequest,
    GoogleOAuthUrlResponse,
    LoginRequest,
    MeResponse,
    MicrosoftOAuthCallbackRequest,
    MicrosoftOAuthUrlResponse,
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
    RevokedTokenModel,
    TokenType,
    UserModel,
    VerificationTokenModel,
)
from identity.services.email_service import get_email_service
from identity.services.signup import _hash_password, _verify_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["identity"])


def _create_token(user_id: UUID, org_id: UUID, secret_key: str) -> tuple[str, str]:
    """Create a JWT token valid for 7 days. Returns (token, jti)."""
    now = datetime.now(tz=UTC)
    expires = now + timedelta(days=7)
    jti = str(uuid.uuid4())
    payload = {
        "sub": str(user_id),
        "org": str(org_id),
        "jti": jti,
        "iat": now.timestamp(),
        "exp": expires.timestamp(),
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token, jti


def _decode_token(token: str, secret_key: str) -> dict[str, Any]:
    """Decode and verify a JWT token."""
    try:
        return jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


async def _is_token_revoked(jti: str) -> bool:
    """Check if a token has been revoked."""
    async with SessionLocal() as session:
        result = await session.execute(
            select(RevokedTokenModel).where(RevokedTokenModel.token_jti == jti)
        )
        return result.scalar_one_or_none() is not None


@router.post("/check-email", response_model=EmailAvailabilityResponse)
async def check_email_availability(
    body: EmailAvailabilityRequest,
) -> EmailAvailabilityResponse:
    """Check if an email is available for signup."""
    async with SessionLocal() as session:
        result = await session.execute(select(UserModel).where(UserModel.email == body.email))
        user = result.scalar_one_or_none()
        if user:
            return EmailAvailabilityResponse(
                available=False,
                message="Email already in use",
            )
        return EmailAvailabilityResponse(
            available=True,
            message="Email is available",
        )


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

            token, _jti = _create_token(user.id, org.id, settings.secret_key)
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

        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not _verify_password(body.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not _verify_password(body.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check if account is active (not deleted/deactivated)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated. Contact support to reactivate.",
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

        token, _jti = _create_token(user.id, membership.organization_id, settings.secret_key)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            organization_id=membership.organization_id,
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_endpoint(request: Request, settings: SettingsDep) -> None:
    """Revoke the current session token by adding it to the revocation list."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = auth_header[7:]
    try:
        payload = _decode_token(token, settings.secret_key)
    except HTTPException:
        return

    jti = payload.get("jti")
    user_id = UUID(payload["sub"])

    if not jti:
        return

    now = datetime.now(tz=UTC)
    expires = datetime.fromtimestamp(payload["exp"], tz=UTC)

    async with SessionLocal() as session:
        try:
            revoked_token = RevokedTokenModel(
                user_id=user_id,
                token_jti=jti,
                revoked_at=now,
                expires_at=expires,
            )
            session.add(revoked_token)
            await session.commit()
        except IntegrityError:
            await session.rollback()


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

    # Check if token has been revoked
    jti = payload.get("jti")
    if jti and await _is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

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
async def forgot_password_endpoint(
    body: ForgotPasswordRequest,
    request: Request,
) -> ForgotPasswordResponse:
    """Generate a password reset token and send it to the user's email.

    Returns a success message without revealing if the email exists.
    """
    now = datetime.now(tz=UTC)
    expires = now + timedelta(hours=24)

    # Extract device and IP from request headers
    user_agent = request.headers.get("user-agent", "Unknown")
    client_ip = request.headers.get(
        "x-forwarded-for", request.client.host if request.client else "Unknown"
    )

    async with SessionLocal() as session:
        # Query user by email
        result = await session.execute(select(UserModel).where(UserModel.email == body.email))
        user = result.scalar_one_or_none()

        # Generate token regardless of user existence (security best practice)
        token = secrets.token_urlsafe(32)

        # Only send email if account exists AND is active (not deleted)
        if user and user.is_active:
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
                        request_device=user_agent,
                        request_ip=client_ip,
                    )
                )

                return ForgotPasswordResponse(
                    message="Check your email for password reset instructions",
                    account_exists=True,
                )

            except IntegrityError as e:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create reset token",
                ) from e

        # Account doesn't exist or is deleted - suggest creating one
        return ForgotPasswordResponse(
            message="No account found with this email. Would you like to create one?",
            account_exists=False,
        )


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

            # Reactivate account if it was deactivated (password reset re-enables access)
            if not user.is_active:
                user.is_active = True

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
            jwt_token, _jti = _create_token(
                user.id, membership.organization_id, settings.secret_key
            )
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
    """Generate and return the Google OAuth authorization URL."""
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

        if token_response.status_code != 200:
            error_detail = token_response.text
            logger.error(
                f"Google token exchange failed: {token_response.status_code} - {error_detail}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to exchange authorization code: {error_detail}",
            )

        token_data = token_response.json()

        # Verify ID token and get user info
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )

        if user_response.status_code != 200:
            error_detail = user_response.text
            logger.error(
                f"Google userinfo retrieval failed: {user_response.status_code} - {error_detail}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to get user info from Google: {error_detail}",
            )

        user_info = user_response.json()
        google_id = user_info.get("id")
        # Use signup email if provided (from signup form), otherwise use Google's email
        email = body.signup_email or user_info.get("email")
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
                # Email already exists - reject to prevent account confusion
                # User should use regular login or password reset instead
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use. Please log in with your existing account.",
                )
            else:
                # Create new user with Google OAuth
                try:
                    # Create organization for new user
                    slug = email.split("@")[0].lower()
                    # Use provided org_name or auto-generate from name
                    org_display_name = body.org_name or f"{name}'s Portfolio"
                    org = OrganizationModel(
                        name=org_display_name,
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
                        email_verified=False,
                        last_login_at=now,
                    )
                    session.add(user)
                    await session.flush()

                    # Create default portfolio
                    portfolio = PortfolioModel(
                        organization_id=org.id,
                        name="Default Portfolio",
                        description="",
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

                    # Send verification email asynchronously
                    email_service = get_email_service()
                    asyncio.create_task(
                        email_service.send_verification_email(
                            user.email, user.full_name, verify_token
                        )
                    )
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
        user_membership: OrgMembershipModel | None = membership_result.scalars().first()

        if not user_membership:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User has no organization membership",
            )

        token, _jti = _create_token(user.id, user_membership.organization_id, settings.secret_key)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            organization_id=user_membership.organization_id,
        )


@router.get("/microsoft/url", response_model=MicrosoftOAuthUrlResponse)
async def microsoft_oauth_url_endpoint(settings: SettingsDep) -> MicrosoftOAuthUrlResponse:
    """Generate and return the Microsoft OAuth authorization URL."""
    if not settings.microsoft_oauth_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Microsoft OAuth not configured",
        )

    params = {
        "client_id": settings.microsoft_oauth_client_id,
        "redirect_uri": f"{settings.frontend_url}/auth/microsoft/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "response_mode": "query",
    }
    url = f"https://login.microsoftonline.com/{settings.microsoft_oauth_tenant}/oauth2/v2.0/authorize?{urlencode(params)}"
    return MicrosoftOAuthUrlResponse(url=url)


@router.post("/microsoft/callback", response_model=TokenResponse)
async def microsoft_oauth_callback_endpoint(
    body: MicrosoftOAuthCallbackRequest,
    settings: SettingsDep,
) -> TokenResponse:
    """Exchange Microsoft authorization code for user token."""
    if not settings.microsoft_oauth_client_id or not settings.microsoft_oauth_client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Microsoft OAuth not configured",
        )

    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_response = await client.post(
            f"https://login.microsoftonline.com/{settings.microsoft_oauth_tenant}/oauth2/v2.0/token",
            data={
                "code": body.code,
                "client_id": settings.microsoft_oauth_client_id,
                "client_secret": settings.microsoft_oauth_client_secret,
                "redirect_uri": f"{settings.frontend_url}/auth/microsoft/callback",
                "grant_type": "authorization_code",
                "scope": "openid email profile",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to exchange authorization code",
            )

        token_data = token_response.json()

        # Get user info from Microsoft Graph
        user_response = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to get user info from Microsoft",
            )

        user_info = user_response.json()
        microsoft_id = user_info.get("id")
        # Use signup email if provided (from signup form), otherwise use Microsoft's email
        email = body.signup_email or user_info.get("userPrincipalName")
        name = user_info.get("displayName", "Microsoft User")

    if not microsoft_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required info from Microsoft",
        )

    now = datetime.now(tz=UTC)

    async with SessionLocal() as session:
        # Try to find user by microsoft_id first
        result = await session.execute(
            select(UserModel).where(UserModel.microsoft_id == microsoft_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Existing Microsoft OAuth user
            user.last_login_at = now
            await session.commit()
        else:
            # Check if user exists by email
            email_result = await session.execute(select(UserModel).where(UserModel.email == email))
            email_user = email_result.scalar_one_or_none()

            if email_user:
                # Email already exists - reject to prevent account confusion
                # User should use regular login or password reset instead
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use. Please log in with your existing account.",
                )
            else:
                # Create new user with Microsoft OAuth
                try:
                    # Create organization for new user
                    slug = email.split("@")[0].lower()
                    # Use provided org_name or auto-generate from name
                    org_display_name = body.org_name or f"{name}'s Portfolio"
                    org = OrganizationModel(
                        name=org_display_name,
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
                        microsoft_id=microsoft_id,
                        password_hash=None,
                        auth_method=AuthMethod.MICROSOFT_SSO,
                        is_active=True,
                        email_verified=False,
                        last_login_at=now,
                    )
                    session.add(user)
                    await session.flush()

                    # Create default portfolio
                    portfolio = PortfolioModel(
                        organization_id=org.id,
                        name="Default Portfolio",
                        description="",
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

                    # Send verification email asynchronously
                    email_service = get_email_service()
                    asyncio.create_task(
                        email_service.send_verification_email(
                            user.email, user.full_name, verify_token
                        )
                    )
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
        user_membership: OrgMembershipModel | None = membership_result.scalars().first()

        if not user_membership:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User has no organization membership",
            )

        token, _jti = _create_token(user.id, user_membership.organization_id, settings.secret_key)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            organization_id=user_membership.organization_id,
        )


# ─── Organization endpoints ───────────────────────────────────────────────────

org_router = APIRouter(prefix="/organizations", tags=["organizations"])


class OrganizationUpdateRequest:
    """Request to update organization settings."""

    def __init__(self, name: str, slug: str, timezone: str = "UTC"):
        self.name = name
        self.slug = slug
        self.timezone = timezone


@org_router.put("/{organization_id}")
async def update_organization(
    organization_id: UUID, name: str, slug: str, timezone: str = "UTC"
) -> OrganizationOut:
    """Update organization settings."""
    async with SessionLocal() as session:
        result = await session.execute(
            select(OrganizationModel).where(OrganizationModel.id == organization_id)
        )
        org = result.scalar_one_or_none()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        org.name = name
        org.slug = slug

        await session.commit()
        await session.refresh(org)

        return OrganizationOut(
            id=org.id,
            name=org.name,
            slug=org.slug,
        )


router.include_router(org_router)
