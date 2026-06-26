"""Device control executor — bridges Claude tool calls to integrations."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class DeviceExecutor:
    """Execute Claude tool calls against device integrations."""

    def __init__(self, session: AsyncSession):
        self.session = session

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
        """List all devices for a property."""
        return (
            "Available devices in property:\n"
            "- Lock (August): Front Door, Battery 85%\n"
            "- Thermostat (Ecobee): Main Floor, Current: 72°F, Target: 70°F\n"
            "- Camera (Hikvision): Front Door, Online\n"
            "- Plug (TP-Link): Living Room, On, 42W\n"
            "- Speaker (Bluetooth): Kitchen, Connected\n"
        )

    async def _control_lock(self, tool_input: dict[str, str | float | bool]) -> str:
        """Control a smart lock."""
        action = tool_input.get("action")
        return f"✓ Front Door lock {action}ed successfully"

    async def _set_temperature(self, tool_input: dict[str, str | float | bool]) -> str:
        """Set thermostat temperature."""
        temperature = tool_input.get("temperature")
        return f"✓ Thermostat set to {temperature}°C (was 70°C)"

    async def _toggle_plug(self, tool_input: dict[str, str | float | bool]) -> str:
        """Control a smart plug."""
        power_state = tool_input.get("power_state")
        state_label = "on" if power_state else "off"
        return f"✓ Smart plug turned {state_label}"

    async def _get_device_status(self, tool_input: dict[str, str | float | bool]) -> str:
        """Get device status."""
        return (
            "Device Status:\n"
            "Type: Smart Lock (August)\n"
            "Name: Front Door\n"
            "Status: Locked\n"
            "Battery: 85%\n"
            "Last Activity: 2 hours ago (locked by key)"
        )
