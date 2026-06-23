"""Identity & Access table models.

The Organization aggregate reuses the existing ``organisations`` table (defined
in ``models.database``); this module adds the User, Portfolio, OrgMembership and
Session tables needed for signup, login and session management. Roles and auth
methods are stored as strings — see ``identity.enums`` for the allowed values.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from identity.enums import AuthMethod, OrgRole


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    password_hash: str
    auth_method: str = Field(default=AuthMethod.PASSWORD.value)
    is_active: bool = Field(default=True)
    is_tenant_only: bool = Field(default=False)
    last_login_at: datetime | None = None
    created_at: datetime | None = Field(default_factory=datetime.utcnow)


class Portfolio(SQLModel, table=True):
    __tablename__ = "portfolios"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organisation_id: UUID = Field(foreign_key="organisations.id", index=True)
    name: str
    description: str | None = None
    is_default: bool = Field(default=False)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    archived_at: datetime | None = None


class OrgMembership(SQLModel, table=True):
    __tablename__ = "org_memberships"
    __table_args__ = (UniqueConstraint("user_id", "organisation_id", name="uq_org_membership"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    organisation_id: UUID = Field(foreign_key="organisations.id", index=True)
    org_role: str = Field(default=OrgRole.OWNER.value)
    joined_at: datetime | None = Field(default_factory=datetime.utcnow)
    invited_by: UUID | None = None


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    active_organisation_id: UUID = Field(foreign_key="organisations.id")
    auth_method: str = Field(default=AuthMethod.PASSWORD.value)
    issued_at: datetime | None = Field(default_factory=datetime.utcnow)
    expires_at: datetime
