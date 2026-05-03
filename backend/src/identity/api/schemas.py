from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=72)
    org_name: str = Field(min_length=1, max_length=255)
    legal_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    organization_id: UUID


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str


class OrganizationOut(BaseModel):
    id: UUID
    name: str
    slug: str


class MeResponse(BaseModel):
    user: UserOut
    organization: OrganizationOut
