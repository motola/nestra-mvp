"""Command execution and management API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from db import SessionLocal
from property.api.command_schemas import (
    CommandCreate,
    CommandHistoryItem,
    CommandHistoryList,
    CommandList,
    CommandRead,
)
from property.commands.executor import CommandExecutor
from property.domain.command import CommandPriority, CommandStatus, CommandType
from property.persistence.capability_repository import CapabilityRepository
from property.persistence.command_execution_log_repository import CommandExecutionLogRepository
from property.persistence.command_repository import CommandRepository
from property.persistence.device_repository import DeviceRepository

router = APIRouter(prefix="/commands", tags=["commands"])


@router.post("/devices/{device_id}/commands", response_model=CommandRead)
async def execute_device_command(
    device_id: UUID,
    request: CommandCreate,
) -> CommandRead:
    """Execute a command on a device.

    Creates a command, validates it, and executes it immediately.

    Args:
        device_id: Device to command
        request: Command request

    Returns:
        CommandRead with execution status
    """
    async with SessionLocal() as db:
        device_repo = DeviceRepository(db)
        capability_repo = CapabilityRepository(db)
        command_repo = CommandRepository(db)
        executor = CommandExecutor(db)

        # Get device
        device = await device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Validate device is online
        if not device.online:
            raise HTTPException(status_code=400, detail="Device is offline")

        # Get capability
        capability = await capability_repo.get_by_code(request.capability_code)
        if not capability:
            raise HTTPException(status_code=422, detail="Capability not supported")

        # Create command
        now = datetime.now(UTC)
        from property.domain.command import Command

        command = Command(
            organization_id=device.organization_id,
            device_id=device_id,
            integration_id=device.integration_id,
            capability_code=request.capability_code,
            command_type=CommandType(request.command_type),
            parameters=request.parameters,
            priority=CommandPriority(request.priority),
            status=CommandStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

        # Save command
        saved_command = await command_repo.create(command)
        if not saved_command.id:
            raise HTTPException(status_code=500, detail="Failed to create command")

        # Execute command
        await executor.execute_command(saved_command, device, capability)

        # Get updated command
        updated = await command_repo.get_by_id(saved_command.id)
        if not updated or not updated.id or not updated.created_at or not updated.updated_at:
            raise HTTPException(status_code=500, detail="Failed to retrieve command")

        return CommandRead(
            id=updated.id,
            organization_id=updated.organization_id,
            device_id=updated.device_id,
            integration_id=updated.integration_id,
            capability_code=updated.capability_code,
            command_type=str(updated.command_type),
            parameters=updated.parameters,
            priority=str(updated.priority),
            status=str(updated.status),
            result=updated.result,
            error_message=updated.error_message,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
            executed_at=updated.executed_at,
        )


@router.get("/devices/{device_id}/commands", response_model=CommandList)
async def get_device_commands(
    device_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> CommandList:
    """Get command history for a device.

    Args:
        device_id: Device to get commands for
        skip: Number of items to skip
        limit: Maximum items to return

    Returns:
        CommandList with paginated command history
    """
    async with SessionLocal() as db:
        device_repo = DeviceRepository(db)
        command_repo = CommandRepository(db)

        # Verify device exists
        device = await device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Get commands
        commands, total = await command_repo.list_by_device(device_id, skip, limit)

        items = []
        for cmd in commands:
            if not cmd.id or not cmd.created_at or not cmd.updated_at:
                continue
            items.append(
                CommandRead(
                    id=cmd.id,
                    organization_id=cmd.organization_id,
                    device_id=cmd.device_id,
                    integration_id=cmd.integration_id,
                    capability_code=cmd.capability_code,
                    command_type=str(cmd.command_type),
                    parameters=cmd.parameters,
                    priority=str(cmd.priority),
                    status=str(cmd.status),
                    result=cmd.result,
                    error_message=cmd.error_message,
                    created_at=cmd.created_at,
                    updated_at=cmd.updated_at,
                    executed_at=cmd.executed_at,
                )
            )

        return CommandList(items=items, total=total, skip=skip, limit=limit)


@router.get("/{command_id}", response_model=CommandRead)
async def get_command(command_id: UUID) -> CommandRead:
    """Get a command by ID.

    Args:
        command_id: ID of command to retrieve

    Returns:
        CommandRead
    """
    async with SessionLocal() as db:
        command_repo = CommandRepository(db)

        command = await command_repo.get_by_id(command_id)
        if not command or not command.id or not command.created_at or not command.updated_at:
            raise HTTPException(status_code=404, detail="Command not found")

        return CommandRead(
            id=command.id,
            organization_id=command.organization_id,
            device_id=command.device_id,
            integration_id=command.integration_id,
            capability_code=command.capability_code,
            command_type=str(command.command_type),
            parameters=command.parameters,
            priority=str(command.priority),
            status=str(command.status),
            result=command.result,
            error_message=command.error_message,
            created_at=command.created_at,
            updated_at=command.updated_at,
            executed_at=command.executed_at,
        )


@router.get("/{command_id}/executions", response_model=CommandHistoryList)
async def get_command_executions(command_id: UUID) -> CommandHistoryList:
    """Get execution history for a command.

    Args:
        command_id: Command to get execution history for

    Returns:
        CommandHistoryList with execution log entries
    """
    async with SessionLocal() as db:
        command_repo = CommandRepository(db)
        log_repo = CommandExecutionLogRepository(db)

        # Verify command exists
        command = await command_repo.get_by_id(command_id)
        if not command:
            raise HTTPException(status_code=404, detail="Command not found")

        # Get execution log
        logs = await log_repo.list_by_command(command_id)

        items = []
        for log in logs:
            if not log.id:
                continue
            items.append(
                CommandHistoryItem(
                    id=log.id,
                    command_id=log.command_id,
                    status=str(log.status),
                    result=log.result,
                    error_message=log.error_message,
                    created_at=log.created_at,
                )
            )

        return CommandHistoryList(items=items, total=len(items))


@router.put("/{command_id}/cancel", response_model=CommandRead)
async def cancel_command(command_id: UUID) -> CommandRead:
    """Cancel a pending command.

    Args:
        command_id: Command to cancel

    Returns:
        CommandRead with cancelled status
    """
    async with SessionLocal() as db:
        command_repo = CommandRepository(db)

        command = await command_repo.cancel(command_id)
        if not command or not command.id or not command.created_at or not command.updated_at:
            raise HTTPException(status_code=404, detail="Command not found or not pending")

        return CommandRead(
            id=command.id,
            organization_id=command.organization_id,
            device_id=command.device_id,
            integration_id=command.integration_id,
            capability_code=command.capability_code,
            command_type=str(command.command_type),
            parameters=command.parameters,
            priority=str(command.priority),
            status=str(command.status),
            result=command.result,
            error_message=command.error_message,
            created_at=command.created_at,
            updated_at=command.updated_at,
            executed_at=command.executed_at,
        )
