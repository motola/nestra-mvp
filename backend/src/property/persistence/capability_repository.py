"""Capability repository — persistence and retrieval of device capabilities."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from property.domain import Capability, DeviceCapability
from property.repository.models import CapabilityModel, DeviceCapabilityModel

logger = logging.getLogger(__name__)


class CapabilityRepository:
    """Persist and retrieve capabilities."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, capability_id: UUID) -> Capability | None:
        """Get a capability by ID."""
        result = await self._session.execute(
            select(CapabilityModel).where(CapabilityModel.id == capability_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def get_by_code(self, code: str) -> Capability | None:
        """Get a capability by code."""
        result = await self._session.execute(
            select(CapabilityModel).where(CapabilityModel.code == code)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def create(self, capability: Capability) -> Capability:
        """Create a new capability."""
        now = datetime.now(UTC)
        model = CapabilityModel(
            id=capability.id,
            code=capability.code,
            name=capability.name,
            description=capability.description,
            category=capability.category,
            created_at=now,
        )
        self._session.add(model)
        await self._session.flush()
        return self._model_to_domain(model)

    async def create_batch(self, capabilities: list[Capability]) -> list[Capability]:
        """Create multiple capabilities."""
        now = datetime.now(UTC)
        models = []
        for cap in capabilities:
            model = CapabilityModel(
                id=cap.id,
                code=cap.code,
                name=cap.name,
                description=cap.description,
                category=cap.category,
                created_at=now,
            )
            models.append(model)
            self._session.add(model)

        await self._session.flush()
        return [self._model_to_domain(m) for m in models]

    async def list_all(self) -> list[Capability]:
        """Get all capabilities."""
        result = await self._session.execute(select(CapabilityModel))
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def list_by_category(self, category: str) -> list[Capability]:
        """Get all capabilities in a category."""
        result = await self._session.execute(
            select(CapabilityModel).where(CapabilityModel.category == category)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    @staticmethod
    def _model_to_domain(model: CapabilityModel) -> Capability:
        """Convert ORM model to domain model."""
        return Capability(
            id=model.id,
            code=model.code,
            name=model.name,
            description=model.description,
            category=model.category,
            created_at=model.created_at,
        )


class DeviceCapabilityRepository:
    """Persist and retrieve device capabilities."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, device_capability_id: UUID) -> DeviceCapability | None:
        """Get a device capability by ID."""
        result = await self._session.execute(
            select(DeviceCapabilityModel).where(DeviceCapabilityModel.id == device_capability_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_domain(model) if model else None

    async def create(self, device_capability: DeviceCapability) -> DeviceCapability:
        """Create a new device capability."""
        now = datetime.now(UTC)
        model = DeviceCapabilityModel(
            id=device_capability.id,
            device_id=device_capability.device_id,
            capability_id=device_capability.capability_id,
            created_at=now,
        )
        self._session.add(model)
        await self._session.flush()
        return self._model_to_domain(model)

    async def create_batch(
        self, device_capabilities: list[DeviceCapability]
    ) -> list[DeviceCapability]:
        """Create multiple device capabilities."""
        now = datetime.now(UTC)
        models = []
        for dev_cap in device_capabilities:
            model = DeviceCapabilityModel(
                id=dev_cap.id,
                device_id=dev_cap.device_id,
                capability_id=dev_cap.capability_id,
                created_at=now,
            )
            models.append(model)
            self._session.add(model)

        await self._session.flush()
        return [self._model_to_domain(m) for m in models]

    async def list_by_device(self, device_id: UUID) -> list[DeviceCapability]:
        """Get all capabilities for a device."""
        result = await self._session.execute(
            select(DeviceCapabilityModel).where(DeviceCapabilityModel.device_id == device_id)
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    async def list_by_capability(self, capability_id: UUID) -> list[DeviceCapability]:
        """Get all devices with a capability."""
        result = await self._session.execute(
            select(DeviceCapabilityModel).where(
                DeviceCapabilityModel.capability_id == capability_id
            )
        )
        models = result.scalars().all()
        return [self._model_to_domain(m) for m in models]

    @staticmethod
    def _model_to_domain(model: DeviceCapabilityModel) -> DeviceCapability:
        """Convert ORM model to domain model."""
        return DeviceCapability(
            id=model.id,
            device_id=model.device_id,
            capability_id=model.capability_id,
            created_at=model.created_at,
        )
