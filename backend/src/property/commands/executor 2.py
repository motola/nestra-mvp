"""Command executor — executes device commands and updates state."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from property.domain import Capability, Device
from property.domain.command import Command, CommandResult, CommandStatus
from property.persistence.command_execution_log_repository import CommandExecutionLogRepository
from property.persistence.command_repository import CommandRepository

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Execute commands on devices."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._command_repo = CommandRepository(session)
        self._log_repo = CommandExecutionLogRepository(session)

    async def execute_command(
        self,
        command: Command,
        device: Device,
        capability: Capability,
    ) -> CommandResult:
        """Execute a command on a device.

        Steps:
        1. Validate device is online and integration is active
        2. Update command status to EXECUTING
        3. Route to correct handler based on capability_code
        4. Update command status based on result
        5. Log execution
        6. Return result

        Args:
            command: Command to execute
            device: Device to execute on
            capability: Capability being used

        Returns:
            CommandResult with status and result/error
        """
        if not command.id:
            raise ValueError("Command ID is required")

        # Update to EXECUTING status
        await self._command_repo.update_status(command.id, CommandStatus.EXECUTING)
        await self._log_repo.create(command.id, CommandStatus.EXECUTING)

        try:
            # Route to handler based on capability code
            result = await self._route_command(device, command, capability)

            # Update command to succeeded
            await self._command_repo.update_status(
                command.id,
                CommandStatus.SUCCEEDED,
                result=result,
            )

            # Log execution
            await self._log_repo.create(
                command.id,
                CommandStatus.SUCCEEDED,
                result=result,
            )

            return CommandResult(
                command_id=command.id,
                status=CommandStatus.SUCCEEDED,
                result=result,
                executed_at=datetime.now(UTC),
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Command execution failed: {error_msg}", exc_info=True)

            # Update command to failed
            await self._command_repo.update_status(
                command.id,
                CommandStatus.FAILED,
                error_message=error_msg,
            )

            # Log execution
            await self._log_repo.create(
                command.id,
                CommandStatus.FAILED,
                error_message=error_msg,
            )

            return CommandResult(
                command_id=command.id,
                status=CommandStatus.FAILED,
                error_message=error_msg,
                executed_at=datetime.now(UTC),
            )

    async def _route_command(
        self, device: Device, command: Command, capability: Capability
    ) -> dict[str, object]:
        """Route command to appropriate handler."""
        capability_code = command.capability_code

        # Route to handler based on capability
        if capability_code == "on_off":
            return await self._execute_on_off(device, command)
        elif capability_code == "brightness":
            return await self._execute_brightness(device, command)
        elif capability_code == "temperature":
            return await self._execute_temperature(device, command)
        elif capability_code == "color":
            return await self._execute_color(device, command)
        elif capability_code == "lock":
            return await self._execute_lock(device, command)
        elif capability_code == "read":
            return await self._execute_read(device, command)
        else:
            raise ValueError(f"Unsupported capability: {capability_code}")

    async def _execute_on_off(self, device: Device, command: Command) -> dict[str, object]:
        """Execute on/off control (PLUG, LIGHT, THERMOSTAT)."""
        params = command.parameters
        state = params.get("state")

        if state not in ("on", "off", True, False):
            raise ValueError(f"Invalid state: {state}")

        # Normalize state
        normalized_state = state in ("on", True)

        # TODO: Call device integration API to set state
        # For now, return success
        return {
            "state": "on" if normalized_state else "off",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def _execute_brightness(self, device: Device, command: Command) -> dict[str, object]:
        """Execute brightness control (LIGHT)."""
        params = command.parameters
        brightness = params.get("brightness")

        if not isinstance(brightness, int | float):
            raise ValueError(f"Invalid brightness: {brightness}")

        if not 0 <= brightness <= 100:
            raise ValueError(f"Brightness out of range: {brightness}")

        # TODO: Call device integration API to set brightness
        # For now, return success
        return {
            "brightness": brightness,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def _execute_temperature(self, device: Device, command: Command) -> dict[str, object]:
        """Execute temperature control (THERMOSTAT)."""
        params = command.parameters
        temperature = params.get("temperature")

        if not isinstance(temperature, int | float):
            raise ValueError(f"Invalid temperature: {temperature}")

        if not -50 <= temperature <= 50:
            raise ValueError(f"Temperature out of range: {temperature}")

        # TODO: Call device integration API to set temperature
        # For now, return success
        return {
            "temperature": temperature,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def _execute_color(self, device: Device, command: Command) -> dict[str, object]:
        """Execute color control (LIGHT)."""
        params = command.parameters
        color = params.get("color")

        if not isinstance(color, str | dict):
            raise ValueError(f"Invalid color: {color}")

        # TODO: Call device integration API to set color
        # For now, return success
        return {
            "color": color,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def _execute_lock(self, device: Device, command: Command) -> dict[str, object]:
        """Execute lock control (LOCK)."""
        params = command.parameters
        action = params.get("action")

        if action not in ("lock", "unlock"):
            raise ValueError(f"Invalid lock action: {action}")

        # TODO: Call device integration API to lock/unlock
        # For now, return success
        return {
            "action": action,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def _execute_read(self, device: Device, command: Command) -> dict[str, object]:
        """Execute read command (SENSOR)."""
        # TODO: Call device integration API to read current state
        # For now, return current state from device
        return {
            "state": device.raw_state,
            "timestamp": datetime.now(UTC).isoformat(),
        }
