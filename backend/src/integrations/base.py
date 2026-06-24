"""Base integration interface for all vendor integrations."""

from abc import ABC, abstractmethod
from typing import Any


class Integration(ABC):
    """Base class for all vendor integrations."""

    vendor_name: str

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to vendor API."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from vendor API."""
        pass

    @abstractmethod
    async def discover_devices(self) -> list[dict[str, Any]]:
        """Discover devices available from this integration."""
        pass
