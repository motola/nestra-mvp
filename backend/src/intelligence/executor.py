"""Device control executor — bridges Claude tool calls to integrations."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from integrations.registry import create_registry
from integrations.sync import DeviceSyncService
from property.persistence.device_repository import DeviceRepository
from property.repository.models import DeviceModel

logger = logging.getLogger(__name__)


class DeviceExecutor:
    """Execute Claude tool calls against device integrations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._registry = create_registry()
        self._repository = DeviceRepository(session)
        self._sync_service = DeviceSyncService(self._registry, self._repository)

    async def execute_tool(
        self,
        tool_name: str,
        tool_input: dict[str, str | float | bool],
    ) -> str:
        """Execute a device control tool and return result as string."""
        try:
            if tool_name == "list_devices":
                return await self._list_devices(tool_input)
            elif tool_name == "control_lock":
                return await self._control_lock(tool_input)
            elif tool_name == "set_temperature":
                return await self._set_temperature(tool_input)
            elif tool_name == "toggle_plug":
                return await self._toggle_plug(tool_input)
            elif tool_name == "get_device_status":
                return await self._get_device_status(tool_input)
            else:
                return f"Error: Unknown tool {tool_name}"
        except Exception as exc:
            logger.error("Tool execution error: %s", exc)
            return f"Error executing {tool_name}: {str(exc)}"

    async def _list_devices(self, tool_input: dict[str, str | float | bool]) -> str:
        """List all devices for a property from repository."""
        property_id = tool_input.get("property_id")
        if not property_id:
            return "Error: property_id required"

        result = await self.session.execute(
            select(DeviceModel).where(DeviceModel.property_id == UUID(str(property_id)))
        )
        devices = result.scalars().all()

        if not devices:
            return "No devices found for this property."

        lines = ["Available devices:"]
        for device in devices:
            lines.append(
                f"- {device.device_type.value} ({device.vendor}): "
                f"{device.vendor_name or 'Unknown'}, Online: {device.online}"
            )
        return "\n".join(lines)

    async def _control_lock(self, tool_input: dict[str, str | float | bool]) -> str:
        """Control a smart lock."""
        device_id = tool_input.get("device_id")
        action = tool_input.get("action")

        if not device_id or not action:
            return "Error: device_id and action required"

        device = await self._repository.get_by_id(UUID(str(device_id)))
        if not device:
            return f"Error: Device {device_id} not found"

        adapter = self._registry.resolve(device.vendor)
        success = await adapter.execute(device, str(action), {})
        return f"✓ Lock {action}ed successfully" if success else "✗ Lock control failed"

    async def _set_temperature(self, tool_input: dict[str, str | float | bool]) -> str:
        """Set thermostat temperature."""
        device_id = tool_input.get("device_id")
        temperature = tool_input.get("temperature")

        if not device_id or temperature is None:
            return "Error: device_id and temperature required"

        device = await self._repository.get_by_id(UUID(str(device_id)))
        if not device:
            return f"Error: Device {device_id} not found"

        adapter = self._registry.resolve(device.vendor)
        success = await adapter.execute(device, "set_temperature", {"temperature": temperature})
        return f"✓ Thermostat set to {temperature}°C" if success else "✗ Temperature control failed"

    async def _toggle_plug(self, tool_input: dict[str, str | float | bool]) -> str:
        """Control a smart plug."""
        device_id = tool_input.get("device_id")
        power_state = tool_input.get("power_state")

        if not device_id or power_state is None:
            return "Error: device_id and power_state required"

        device = await self._repository.get_by_id(UUID(str(device_id)))
        if not device:
            return f"Error: Device {device_id} not found"

        adapter = self._registry.resolve(device.vendor)
        command = "turn_on" if power_state else "turn_off"
        success = await adapter.execute(device, command, {"power_state": power_state})
        state_label = "on" if power_state else "off"
        return f"✓ Plug turned {state_label}" if success else "✗ Plug control failed"

    async def _get_device_status(self, tool_input: dict[str, str | float | bool]) -> str:
        """Get device status."""
        device_id = tool_input.get("device_id")

        if not device_id:
            return "Error: device_id required"

        device = await self._repository.get_by_id(UUID(str(device_id)))
        if not device:
            return f"Error: Device {device_id} not found"

        return (
            f"Device Status:\n"
            f"Type: {device.device_type.value} ({device.vendor})\n"
            f"Name: {device.vendor_name or 'Unknown'}\n"
            f"Status: {'Online' if device.online else 'Offline'}\n"
            f"Last Sync: {device.last_sync.isoformat()}\n"
            f"State: {device.raw_state}"
        )
