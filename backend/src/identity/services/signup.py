from __future__ import annotations

import re
from datetime import UTC, datetime
from uuid import uuid4

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from identity.domain.organization import Organization, Portfolio
from identity.domain.roles import AuthMethod, OrgRole, OrgStatus, SubscriptionTier
from identity.domain.user import User
from identity.repository.models import (
    OrganizationModel,
    OrgMembershipModel,
    PortfolioModel,
    UserModel,
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(name: str) -> str:
    return _SLUG_RE.sub("-", name.lower()).strip("-")


def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


class SignupResult:
    def __init__(self, user: User, organization: Organization, portfolio: Portfolio) -> None:
        self.user = user
        self.organization = organization
        self.portfolio = portfolio


async def signup(
    session: AsyncSession,
    *,
    email: str,
    full_name: str,
    password: str,
    org_name: str,
    legal_name: str,
) -> SignupResult:
    """Create a User, Organization, default Portfolio, and OrgMembership atomically."""
    now = datetime.now(tz=UTC)

    org_id = uuid4()
    user_id = uuid4()
    portfolio_id = uuid4()
    membership_id = uuid4()

    slug = _slugify(org_name)

    org_row = OrganizationModel(
        id=org_id,
        name=org_name,
        slug=slug,
        legal_name=legal_name,
        status=OrgStatus.ACTIVE,
        subscription_tier=SubscriptionTier.STARTER,
        created_at=now,
    )
    portfolio_row = PortfolioModel(
        id=portfolio_id,
        organization_id=org_id,
        name="Default",
        description="",
        is_default=True,
        created_at=now,
    )
    user_row = UserModel(
        id=user_id,
        email=email,
        full_name=full_name,
        password_hash=_hash_password(password),
        auth_method=AuthMethod.PASSWORD,
        is_active=True,
        is_tenant_only=False,
    )
    membership_row = OrgMembershipModel(
        id=membership_id,
        user_id=user_id,
        organization_id=org_id,
        org_role=OrgRole.OWNER,
        joined_at=now,
    )

    session.add_all([org_row, portfolio_row, user_row, membership_row])
    await session.flush()

    return SignupResult(
        user=User(
            id=user_id,
            email=email,
            full_name=full_name,
            password_hash=user_row.password_hash,
            auth_method=AuthMethod.PASSWORD,
        ),
        organization=Organization(
            id=org_id,
            name=org_name,
            slug=slug,
            legal_name=legal_name,
            status=OrgStatus.ACTIVE,
            subscription_tier=SubscriptionTier.STARTER,
            created_at=now,
        ),
        portfolio=Portfolio(
            id=portfolio_id,
            organization_id=org_id,
            name="Default",
            description="",
            is_default=True,
            created_at=now,
        ),
    )
