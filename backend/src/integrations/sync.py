"""DeviceSyncService — the orchestrator that drives a full integration sync.

It is the *caller* that sits on the outside, not a stage in the middle: it
resolves an adapter, asks it to fetch + interpret devices, stamps each one with
sync context via the factory, and upserts it into the repository. The adapter
and the repository never reference each other — the sync service wires them.

Fetch and upsert are injected so the orchestration is testable with no network
and no database.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from integrations.factory import create_device_data
from spire.device import SpireDevice

logger = logging.getLogger(__name__)

# Fetch + interpret a vendor's devices into SpireDevices (an adapter method).
DeviceFetcher = Callable[[], Awaitable[list[SpireDevice]]]
# Insert-or-update one device, keyed on its identity (the repository).
DeviceUpsert = Callable[[SpireDevice], Awaitable[None]]


class DeviceSyncService:
    """Drives one integration sync: fetch → stamp context → upsert."""

    def __init__(self, *, fetch: DeviceFetcher, upsert: DeviceUpsert) -> None:
        self._fetch = fetch
        self._upsert = upsert

    async def sync_integration(
        self,
        *,
        organization_id: str | None = None,
        property_id: str | None = None,
        integration_id: str | None = None,
    ) -> int:
        """Run one integration sync; return the number of devices synced."""
        devices = await self._fetch()
        for device in devices:
            stamped = create_device_data(
                device,
                organization_id=organization_id,
                property_id=property_id,
                integration_id=integration_id,
            )
            await self._upsert(stamped)
        logger.info("Synced %d devices for integration %s", len(devices), integration_id)
        return len(devices)
