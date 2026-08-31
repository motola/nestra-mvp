"""Magic link token repository for share-based access."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from property.domain.tokens import MagicLinkToken
from property.repository.models import MagicLinkTokenModel

logger = logging.getLogger(__name__)


class MagicLinkTokenRepository:
    """Persist and retrieve magic link tokens."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_token(self, token: str) -> MagicLinkToken | None:
        """Get a token by its value."""
        result = await self._session.execute(
            select(MagicLinkTokenModel).where(MagicLinkTokenModel.token == token)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def get_by_id(self, token_id: UUID) -> MagicLinkToken | None:
        """Get a token by ID."""
        result = await self._session.execute(
            select(MagicLinkTokenModel).where(MagicLinkTokenModel.id == token_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def create(self, magic_token: MagicLinkToken) -> MagicLinkToken:
        """Create a new magic link token."""
        magic_token.id = uuid4()
        magic_token.created_at = datetime.now(UTC)

        model = MagicLinkTokenModel(
            id=magic_token.id,
            organization_id=magic_token.organization_id,
            device_id=magic_token.device_id,
            access_type=magic_token.access_type,
            token=magic_token.token,
            created_by_user_id=magic_token.created_by_user_id,
            claimed_by_user_id=magic_token.claimed_by_user_id,
            claimed_at=magic_token.claimed_at,
            expires_at=magic_token.expires_at,
            created_at=magic_token.created_at,
            revoked_at=magic_token.revoked_at,
        )
        self._session.add(model)
        await self._session.flush()
        return magic_token

    async def claim_token(self, token: str, user_id: UUID) -> bool:
        """Claim a token by a user."""
        result = await self._session.execute(
            select(MagicLinkTokenModel).where(MagicLinkTokenModel.token == token)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        now = datetime.now(UTC)

        # Check if not expired
        if model.expires_at < now:
            return False

        # Check if already revoked
        if model.revoked_at is not None:
            return False

        model.claimed_by_user_id = user_id
        model.claimed_at = now
        await self._session.flush()
        return True

    async def list_by_device(
        self, device_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[MagicLinkToken]:
        """List all share links for a device."""
        result = await self._session.execute(
            select(MagicLinkTokenModel)
            .where(
                and_(
                    MagicLinkTokenModel.device_id == device_id,
                    MagicLinkTokenModel.revoked_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def revoke(self, token_id: UUID) -> bool:
        """Revoke a magic link token."""
        result = await self._session.execute(
            select(MagicLinkTokenModel).where(MagicLinkTokenModel.id == token_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        model.revoked_at = datetime.now(UTC)
        await self._session.flush()
        return True

    @staticmethod
    def _model_to_domain(model: MagicLinkTokenModel) -> MagicLinkToken:
        """Convert ORM model to domain model."""
        return MagicLinkToken(
            id=model.id,
            organization_id=model.organization_id,
            device_id=model.device_id,
            access_type=model.access_type,
            token=model.token,
            created_by_user_id=model.created_by_user_id,
            claimed_by_user_id=model.claimed_by_user_id,
            claimed_at=model.claimed_at,
            expires_at=model.expires_at,
            created_at=model.created_at,
            revoked_at=model.revoked_at,
        )
