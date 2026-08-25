from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base
from identity.domain.roles import AuthMethod, OrgRole, OrgStatus, SubscriptionTier


class TokenType(PyEnum):
    """Types of verification tokens."""

    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[OrgStatus] = mapped_column(Enum(OrgStatus, name="org_status"), nullable=False)
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier, name="subscription_tier"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    portfolios: Mapped[list[PortfolioModel]] = relationship(back_populates="organization")
    memberships: Mapped[list[OrgMembershipModel]] = relationship(back_populates="organization")


class PortfolioModel(Base):
    __tablename__ = "portfolios"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[OrganizationModel] = relationship(back_populates="portfolios")

    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_portfolio_org_name"),)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    microsoft_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    auth_method: Mapped[AuthMethod] = mapped_column(
        Enum(AuthMethod, name="auth_method"), nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_tenant_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    memberships: Mapped[list[OrgMembershipModel]] = relationship(
        back_populates="user", foreign_keys="[OrgMembershipModel.user_id]"
    )
    sessions: Mapped[list[SessionModel]] = relationship(back_populates="user")
    verification_tokens: Mapped[list[VerificationTokenModel]] = relationship(
        back_populates="user", foreign_keys="[VerificationTokenModel.user_id]"
    )


class OrgMembershipModel(Base):
    __tablename__ = "org_memberships"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    org_role: Mapped[OrgRole] = mapped_column(Enum(OrgRole, name="org_role"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    invited_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    user: Mapped[UserModel] = relationship(back_populates="memberships", foreign_keys=[user_id])
    organization: Mapped[OrganizationModel] = relationship(back_populates="memberships")

    __table_args__ = (UniqueConstraint("user_id", "organization_id", name="uq_org_membership"),)


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    active_organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    auth_method: Mapped[AuthMethod] = mapped_column(
        Enum(AuthMethod, name="auth_method"), nullable=False
    )
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped[UserModel] = relationship(back_populates="sessions")


class VerificationTokenModel(Base):
    """Tokens for password reset and email verification."""

    __tablename__ = "verification_tokens"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    token_type: Mapped[TokenType] = mapped_column(
        Enum(TokenType, name="token_type"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[UserModel] = relationship(
        back_populates="verification_tokens", foreign_keys=[user_id]
    )


class RevokedTokenModel(Base):
    """Tracks revoked JWT tokens to prevent reuse after logout."""

    __tablename__ = "revoked_tokens"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    token_jti: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UserConsentModel(Base):
    """Tracks user consent for Claude AI data access."""

    __tablename__ = "user_consents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )
    portfolio_access: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    device_access: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    historical_data_access: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consented_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AiConversationModel(Base):
    """Stores AI conversation history."""

    __tablename__ = "ai_conversations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    user_message: Mapped[str] = mapped_column(String(5000), nullable=False)
    ai_response: Mapped[str] = mapped_column(String(5000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AiGeneratedReportModel(Base):
    """Stores reports generated by Claude AI."""

    __tablename__ = "ai_generated_reports"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String(10000), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AiActionLogModel(Base):
    """Audit trail for actions taken by Claude AI."""

    __tablename__ = "ai_action_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    action_status: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
