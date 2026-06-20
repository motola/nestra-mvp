from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from fastapi import APIRouter, HTTPException, status

from config import get_settings
from dependencies import SettingsDep
from identity.api.schemas import (
    LoginRequest,
    MeResponse,
    OrganizationOut,
    SignupRequest,
    TokenResponse,
    UserOut,
)
from identity.services.signup import _hash_password, _verify_password

router = APIRouter(prefix="/auth", tags=["identity"])

# ─── Mock data (remove when database is wired) ────────────────────────────────

# In-memory store for demo — replaced with real DB queries later
_MOCK_USERS: dict[str, dict] = {}
_MOCK_ORGS: dict[UUID, dict] = {}

# Test user for immediate login demo
_TEST_ORG_ID = UUID("12345678-1234-5678-1234-567812345678")
_TEST_USER_ID = UUID("87654321-4321-8765-4321-876543218765")

_MOCK_ORGS[_TEST_ORG_ID] = {
    "id": _TEST_ORG_ID,
    "name": "Test Organization",
    "slug": "test-org",
}

_MOCK_USERS["test@example.com"] = {
    "id": _TEST_USER_ID,
    "email": "test@example.com",
    "full_name": "Test User",
    "password_hash": _hash_password("password123"),
    "org_id": _TEST_ORG_ID,
}


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


def _decode_token(token: str, secret_key: str) -> dict:
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
    # Check if email already registered (mock)
    if body.email in _MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already in use",
        )

    # Create mock user and org
    user_id = uuid4()
    org_id = uuid4()

    _MOCK_ORGS[org_id] = {
        "id": org_id,
        "name": body.org_name,
        "slug": body.org_name.lower().replace(" ", "-"),
    }

    _MOCK_USERS[body.email] = {
        "id": user_id,
        "email": body.email,
        "full_name": body.full_name,
        "password_hash": _hash_password(body.password),
        "org_id": org_id,
    }

    token = _create_token(user_id, org_id, settings.secret_key)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        organization_id=org_id,
    )


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(
    body: LoginRequest,
    settings: SettingsDep,
) -> TokenResponse:
    """Authenticate with email + password and return a JWT."""
    # Check mock user
    user = _MOCK_USERS.get(body.email)
    if not user or not _verify_password(body.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = _create_token(user["id"], user["org_id"], settings.secret_key)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        organization_id=user["org_id"],
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

    # Find user in mock store
    user = next((u for u in _MOCK_USERS.values() if u["id"] == user_id), None)
    org = _MOCK_ORGS.get(org_id)

    if not user or not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or organization not found",
        )

    return MeResponse(
        user=UserOut(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
        ),
        organization=OrganizationOut(
            id=org["id"],
            name=org["name"],
            slug=org["slug"],
        ),
    )
