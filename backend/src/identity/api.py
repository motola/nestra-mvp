"""Identity HTTP endpoints — signup, login, logout, current user."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from api.dependencies import SessionDep
from identity import service
from identity.models import User
from identity.security import decode_access_token
from models.database import Organisation

router = APIRouter(tags=["identity"])


class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str
    organization_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StatusResponse(BaseModel):
    status: str


class OrganizationOut(BaseModel):
    id: UUID
    name: str


class MeResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    organization: OrganizationOut | None = None


async def current_user(
    session: SessionDep,
    authorization: Annotated[str | None, Header()] = None,
) -> tuple[User, dict]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    payload = decode_access_token(authorization.split(" ", 1)[1])
    if payload is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = await service.get_user_by_id(session, UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User no longer active")
    return user, payload


CurrentUser = Annotated[tuple[User, dict], Depends(current_user)]


@router.post("/auth/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest, session: SessionDep) -> TokenResponse:
    try:
        _, _, token = await service.signup(
            session,
            email=body.email,
            password=body.password,
            full_name=body.full_name,
            organization_name=body.organization_name,
        )
    except service.EmailAlreadyRegistered:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered") from None
    return TokenResponse(access_token=token)


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: SessionDep) -> TokenResponse:
    try:
        token = await service.login(session, email=body.email, password=body.password)
    except service.InvalidCredentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password") from None
    return TokenResponse(access_token=token)


@router.post("/auth/logout", response_model=StatusResponse)
async def logout(current: CurrentUser) -> StatusResponse:
    # Stateless JWT: the client discards its token. Server-side session
    # revocation arrives with the tenant-scope work in A3.
    return StatusResponse(status="logged_out")


@router.get("/me", response_model=MeResponse)
async def me(current: CurrentUser, session: SessionDep) -> MeResponse:
    user, payload = current
    organization: OrganizationOut | None = None
    org_id = payload.get("org")
    if org_id:
        org = await session.get(Organisation, UUID(org_id))
        if org is not None:
            organization = OrganizationOut(id=org.id, name=org.name)
    return MeResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        organization=organization,
    )
