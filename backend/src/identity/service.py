"""Identity use cases — signup, login, session issuance."""

from __future__ import annotations

from datetime import datetime
from typing import Final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from identity.enums import AuthMethod, OrgRole
from identity.models import OrgMembership, Portfolio, Session, User
from identity.security import ACCESS_TOKEN_TTL, create_access_token, hash_password, verify_password
from models.database import Organisation

_DEFAULT_PORTFOLIO_NAME: Final[str] = "Default portfolio"


class EmailAlreadyRegistered(Exception):
    """Raised when signup is attempted with an email that already exists."""


class InvalidCredentials(Exception):
    """Raised when login credentials do not match an active user."""


async def signup(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    full_name: str,
    organization_name: str | None,
) -> tuple[User, Organisation, str]:
    """Create an Organisation, owner User, default Portfolio and membership atomically."""
    if await session.scalar(select(User).where(col(User.email) == email)) is not None:
        raise EmailAlreadyRegistered(email)

    org = Organisation(name=organization_name or f"{full_name}'s organisation")
    session.add(org)
    await session.flush()

    user = User(
        email=email,
        full_name=full_name,
        password_hash=hash_password(password),
        auth_method=AuthMethod.PASSWORD.value,
    )
    session.add(user)
    await session.flush()

    session.add(Portfolio(organisation_id=org.id, name=_DEFAULT_PORTFOLIO_NAME, is_default=True))
    session.add(
        OrgMembership(user_id=user.id, organisation_id=org.id, org_role=OrgRole.OWNER.value)
    )

    token = await _issue_session(session, user, org.id)
    await session.commit()
    return user, org, token


async def login(session: AsyncSession, *, email: str, password: str) -> str:
    user = await session.scalar(select(User).where(col(User.email) == email))
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        raise InvalidCredentials
    org_id = await session.scalar(
        select(col(OrgMembership.organisation_id)).where(col(OrgMembership.user_id) == user.id)
    )
    if org_id is None:
        raise InvalidCredentials
    user.last_login_at = datetime.utcnow()
    token = await _issue_session(session, user, org_id)
    await session.commit()
    return token


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User | None:
    return await session.get(User, user_id)


async def _issue_session(session: AsyncSession, user: User, org_id: UUID) -> str:
    record = Session(
        user_id=user.id,
        active_organisation_id=org_id,
        auth_method=AuthMethod.PASSWORD.value,
        expires_at=datetime.utcnow() + ACCESS_TOKEN_TTL,
    )
    session.add(record)
    await session.flush()
    return create_access_token({"sub": str(user.id), "sid": str(record.id), "org": str(org_id)})
