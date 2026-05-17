from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from identity.api.schemas import (
    LoginRequest,
    MeResponse,
    SignupRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["identity"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest) -> TokenResponse:
    """Create a new user, organization, default portfolio, and membership."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Database not yet available — wired in 5d after migrations",
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    """Authenticate with email + password and return a JWT."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Database not yet available — wired in 5d after migrations",
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> None:
    """Revoke the current session token."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Database not yet available — wired in 5d after migrations",
    )


@router.get("/me", response_model=MeResponse)
async def me() -> MeResponse:
    """Return the authenticated user and their active organization."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Database not yet available — wired in 5d after migrations",
    )
