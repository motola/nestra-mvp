"""
Vendor integration abstraction layer.

Rule: every vendor client must extend BaseVendorAdapter.
Every method must return SpireDevice — never a vendor-specific type.
Nothing outside this package should ever reference a vendor field name.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from spire import SpireDevice


class BaseVendorAdapter(ABC):
    """
    Abstract base class for all vendor integrations.

    Implementing classes: GoveeAdapter, ShellyAdapter, ShellyLocalAdapter, LIFXAdapter.
    Each adapter wraps a vendor-specific HTTP client and a normaliser, presenting
    a single clean interface to the rest of the platform.
    """

    @abstractmethod
    async def list_devices(self) -> list[SpireDevice]:
        """Return all devices for this vendor account, fully normalised."""
        ...

    @abstractmethod
    async def get_device_state(self, device_id: str) -> SpireDevice:
        """Return the current state of a single device by its Alphacon device ID."""
        ...

    @abstractmethod
    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        """
        Send a control command to a device.

        The command dict uses Alphacon keys, not vendor keys.
        Example: {"action": "turn_on"}, {"action": "set_brightness", "value": 80}

        Returns True if the vendor confirmed success.
        """
        ...
