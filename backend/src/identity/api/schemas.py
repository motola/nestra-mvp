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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    account_exists: bool = True


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=72)


class VerifyEmailRequest(BaseModel):
    token: str


class VerifyEmailResponse(BaseModel):
    message: str


class GoogleOAuthUrlResponse(BaseModel):
    url: str


class GoogleOAuthCallbackRequest(BaseModel):
    code: str
    org_name: str | None = None  # Optional: provided by frontend for new signups
    signup_email: str | None = None  # Optional: email from signup form instead of provider's


class GoogleOAuthToken(BaseModel):
    access_token: str
    expires_in: int
    scope: str
    token_type: str
    id_token: str


class GoogleOAuthUserInfo(BaseModel):
    sub: str
    email: EmailStr
    name: str
    picture: str | None = None
    email_verified: bool


class MicrosoftOAuthUrlResponse(BaseModel):
    url: str


class MicrosoftOAuthCallbackRequest(BaseModel):
    code: str
    org_name: str | None = None  # Optional: provided by frontend for new signups
    signup_email: str | None = None  # Optional: email from signup form instead of provider's


class MicrosoftOAuthUserInfo(BaseModel):
    id: str
    userPrincipalName: str
    displayName: str


class EmailAvailabilityRequest(BaseModel):
    email: EmailStr


class EmailAvailabilityResponse(BaseModel):
    available: bool
    message: str


class UserConsentRequest(BaseModel):
    portfolio_access: bool
    device_access: bool
    historical_data_access: bool


class UserConsentResponse(BaseModel):
    portfolio_access: bool
    device_access: bool
    historical_data_access: bool


class AiChatRequest(BaseModel):
    message: str


class AiActionResponse(BaseModel):
    action_type: str
    status: str
    details: str


class AiChatResponse(BaseModel):
    response: str
    actions: list[AiActionResponse] = []


class AiReportResponse(BaseModel):
    id: UUID
    title: str
    content: str
    report_type: str
    created_at: str
