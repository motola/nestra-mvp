from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from identity.domain.roles import AuthMethod, OrgRole


class User(BaseModel):
    id: UUID
    email: str
    full_name: str
    password_hash: str
    auth_method: AuthMethod
    last_login_at: datetime | None = None
    is_active: bool = True
    is_tenant_only: bool = False

    def can(self, action: str, resource: object) -> bool:
        raise NotImplementedError


class OrgMembership(BaseModel):
    id: UUID
    user_id: UUID
    organization_id: UUID
    org_role: OrgRole
    joined_at: datetime
    invited_by: UUID | None = None


class Session(BaseModel):
    id: UUID
    user_id: UUID
    active_organization_id: UUID
    auth_method: AuthMethod
    issued_at: datetime
    expires_at: datetime
