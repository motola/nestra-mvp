"""Device sync service — orchestrates adapter → repository pipeline."""

from __future__ import annotations

import logging
from typing import cast
from uuid import UUID

from integrations.registry import AdapterRegistry
from property.domain import Device
from property.persistence.device_repository import DeviceRepository

logger = logging.getLogger(__name__)


class DeviceSyncService:
    """Orchestrate device sync: resolve adapter → fetch → persist.

    Does not contain vendor-specific logic. Each step is a single call
    to the appropriate abstraction.
    """

    def __init__(self, registry: AdapterRegistry, repository: DeviceRepository):
        self._registry = registry
        self._repository = repository

    async def sync_integration(
        self,
        *,
        vendor: str,
        organization_id: UUID,
        property_id: UUID,
        integration_id: UUID,
        credentials: dict[str, str] | None = None,
    ) -> list[Device]:
        """Sync all devices for an integration.

        1. Resolve adapter by vendor name.
        2. Fetch devices from vendor (interpreted, in-memory).
        3. Upsert each device to repository (O(1) per device).

        Returns the persisted devices with assigned IDs.
        """
        adapter = self._registry.resolve(vendor)
        logger.info("Syncing %s devices for integration %s", vendor, integration_id)

        # Pass vendor-specific credential to adapter
        # Each vendor adapter expects different credential names:
        # lifx: api_token, govee: api_key, meross: access_token, shelly: auth_token
        fetch_kwargs = {
            "organization_id": organization_id,
            "property_id": property_id,
            "integration_id": integration_id,
        }
        if credentials:
            fetch_kwargs.update(cast(dict[str, object], credentials))

        devices = await adapter.fetch_devices(**fetch_kwargs)
        logger.info("Fetched %d devices from %s", len(devices), vendor)

        persisted: list[Device] = []
        for device in devices:
            stored = await self._repository.upsert(device)
            persisted.append(stored)

        logger.info("Persisted %d devices for integration %s", len(persisted), integration_id)
        return persisted
