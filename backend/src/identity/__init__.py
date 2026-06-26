"""Identity & Access bounded context.

Public surface — other contexts import identity types only from here, never from
submodules. (Repository/service/api layers are added in later batches.)
"""

from __future__ import annotations

from identity.enums import AuthMethod, OrgRole, PortfolioRole, PropertyRole
from identity.models import OrgMembership, Portfolio, Session, User


from identity.domain.organization import Organization, Portfolio
from identity.domain.roles import (
    AuthMethod,
    OrgRole,
    OrgStatus,
    PortfolioRole,
    PropertyRole,
    SubscriptionTier,
    TenantRole,
)
from identity.domain.user import OrgMembership, Session, User

__all__ = [
    "AuthMethod",
    "OrgMembership",
    "OrgRole",
    "OrgStatus",
    "Organization",
    "Portfolio",
    "PortfolioRole",
    "PropertyRole",
    "Session",
    "SubscriptionTier",
    "TenantRole",
    "User",
]
