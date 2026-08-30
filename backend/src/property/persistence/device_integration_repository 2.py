"""Device integration repository — persistence and retrieval of device integrations."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from property.domain import DeviceIntegration
from property.repository.models import DeviceIntegrationModel

logger = logging.getLogger(__name__)


class DeviceIntegrationRepository:
    """Persist and retrieve device integrations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_device_id(self, device_id: UUID) -> DeviceIntegration | None:
        """Get device integration by device ID."""
        result = await self._session.execute(
            select(DeviceIntegrationModel).where(DeviceIntegrationModel.device_id == device_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def get_by_id(self, integration_id: UUID) -> DeviceIntegration | None:
        """Get a device integration by ID."""
        result = await self._session.execute(
            select(DeviceIntegrationModel).where(DeviceIntegrationModel.id == integration_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def create(self, device_integration: DeviceIntegration) -> DeviceIntegration:
        """Create a new device integration."""
        now = datetime.now(UTC)
        model = DeviceIntegrationModel(
            id=device_integration.id,
            device_id=device_integration.device_id,
            integration_id=device_integration.integration_id,
            connection_identifier=device_integration.connection_identifier,
            discovered_at=device_integration.discovered_at,
            last_synced_at=device_integration.last_synced_at,
            created_at=now,
            updated_at=now,
        )
        self._session.add(model)
        await self._session.flush()
        return self._model_to_domain(model)

    async def update(self, device_integration: DeviceIntegration) -> DeviceIntegration:
        """Update an existing device integration."""
        result = await self._session.execute(
            select(DeviceIntegrationModel).where(DeviceIntegrationModel.id == device_integration.id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Device integration {device_integration.id} not found")

        model.connection_identifier = device_integration.connection_identifier
        model.last_synced_at = device_integration.last_synced_at
        model.updated_at = datetime.now(UTC)

        await self._session.flush()
        return self._model_to_domain(model)

    async def list_by_integration(self, integration_id: UUID) -> list[DeviceIntegration]:
        """Get all device integrations for an integration."""
        result = await self._session.execute(
            select(DeviceIntegrationModel).where(
                DeviceIntegrationModel.integration_id == integration_id
            )
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def list_by_device(self, device_id: UUID) -> list[DeviceIntegration]:
        """Get all integrations for a device."""
        result = await self._session.execute(
            select(DeviceIntegrationModel).where(DeviceIntegrationModel.device_id == device_id)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    @staticmethod
    def _model_to_domain(model: DeviceIntegrationModel) -> DeviceIntegration:
        """Convert ORM model to domain model."""
        return DeviceIntegration(
            id=model.id,
            device_id=model.device_id,
            integration_id=model.integration_id,
            connection_identifier=model.connection_identifier,
            discovered_at=model.discovered_at,
            last_synced_at=model.last_synced_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
