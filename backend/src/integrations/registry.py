"""Adapter registry — maps vendor strings to adapter instances."""

from __future__ import annotations

from integrations.adapter import IntegrationAdapter
from integrations.august.adapter import AugustAdapter
from integrations.bluetooth.adapter import BluetoothAdapter
from integrations.ecobee.adapter import EcobeeAdapter
from integrations.hikvision.adapter import HikvisionAdapter
from integrations.tplink.adapter import TPLinkAdapter


class UnknownVendorError(Exception):
    """Raised when a vendor is not registered."""

    pass


class AdapterRegistry:
    """Registry of vendor adapters. O(1) lookup by vendor string."""

    def __init__(self, adapters: dict[str, IntegrationAdapter]):
        self._adapters = adapters

    def resolve(self, vendor: str) -> IntegrationAdapter:
        """Resolve a vendor string to its adapter. Raises UnknownVendorError if not found.

        O(1) dict lookup.
        """
        adapter = self._adapters.get(vendor)
        if adapter is None:
            raise UnknownVendorError(f"No adapter registered for vendor: {vendor}")
        return adapter


def create_registry() -> AdapterRegistry:
    """Factory function to create and initialize the adapter registry with all vendors."""
    adapters: dict[str, IntegrationAdapter] = {
        "august": AugustAdapter(),
        "bluetooth": BluetoothAdapter(),
        "ecobee": EcobeeAdapter(),
        "hikvision": HikvisionAdapter(),
        "tplink": TPLinkAdapter(),
    }
    return AdapterRegistry(adapters)
