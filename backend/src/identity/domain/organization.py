from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from identity.domain.roles import OrgStatus, SubscriptionTier


class Organization(BaseModel):
    id: UUID
    name: str
    slug: str
    legal_name: str
    status: OrgStatus
    subscription_tier: SubscriptionTier
    created_at: datetime


class Portfolio(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str
    is_default: bool
    created_at: datetime
    archived_at: datetime | None = None
