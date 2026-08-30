"""Capability discovery for smart home devices."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from property.domain import Capability, Device, DeviceCapability, DeviceType

logger = logging.getLogger(__name__)

# Capability definitions mapped by device type
DEVICE_CAPABILITIES: dict[DeviceType, list[tuple[str, str, str, str]]] = {
    DeviceType.LOCK: [
        ("lock_unlock", "Lock/Unlock", "Lock or unlock the device", "control"),
        ("battery_level", "Battery Level", "Current battery charge level", "sensor"),
        ("lock_state", "Lock State", "Current lock state (locked/unlocked)", "info"),
    ],
    DeviceType.THERMOSTAT: [
        ("temperature_read", "Temperature Reading", "Current ambient temperature", "sensor"),
        ("temperature_set", "Set Temperature", "Set target temperature", "control"),
        ("humidity_read", "Humidity Reading", "Current humidity level", "sensor"),
        ("mode_set", "Mode Control", "Set heating/cooling/auto mode", "control"),
        ("mode_read", "Mode Status", "Current operating mode", "info"),
    ],
    DeviceType.CAMERA: [
        ("video_stream", "Video Stream", "Live video feed", "info"),
        ("recording", "Recording", "Video recording capability", "control"),
        ("night_vision", "Night Vision", "Night vision capability", "info"),
        ("motion_detection", "Motion Detection", "Motion detection capability", "sensor"),
    ],
    DeviceType.PLUG: [
        ("on_off", "On/Off Control", "Turn on or off", "control"),
        ("power_state", "Power State", "Current on/off state", "info"),
        ("power_usage", "Power Usage", "Current power consumption", "sensor"),
    ],
    DeviceType.SENSOR: [
        ("temperature_read", "Temperature Reading", "Current temperature", "sensor"),
        ("humidity_read", "Humidity Reading", "Current humidity", "sensor"),
        ("motion_detection", "Motion Detection", "Motion detected", "sensor"),
        ("light_level", "Light Level", "Ambient light level", "sensor"),
    ],
    DeviceType.SPEAKER: [
        ("volume_control", "Volume Control", "Adjust speaker volume", "control"),
        ("play_pause", "Play/Pause", "Play or pause audio", "control"),
        ("audio_state", "Audio State", "Current playback state", "info"),
    ],
    DeviceType.LIGHT: [
        ("on_off", "On/Off Control", "Turn on or off", "control"),
        ("brightness", "Brightness Control", "Adjust brightness (0-100)", "control"),
        ("color", "Color Control", "Change light color", "control"),
        ("color_temp", "Color Temperature", "Adjust warm/cool tone", "control"),
        ("power_state", "Power State", "Current on/off state", "info"),
    ],
}


async def discover_device_capabilities(device: Device) -> list[Capability]:
    """Discover capabilities for a device based on its type.

    Args:
        device: The device to discover capabilities for

    Returns:
        List of Capability objects representing the device's capabilities
    """
    device_type = device.device_type

    if device_type not in DEVICE_CAPABILITIES:
        logger.warning(f"Unknown device type: {device_type}")
        return []

    capabilities: list[Capability] = []
    for code, name, description, category in DEVICE_CAPABILITIES[device_type]:
        capability = Capability(
            id=None,
            code=code,
            name=name,
            description=description,
            category=category,
            created_at=datetime.now(UTC),
        )
        capabilities.append(capability)

    logger.info(f"Discovered {len(capabilities)} capabilities for device {device.id}")
    return capabilities


async def create_device_capabilities(
    device_id: UUID,
    capabilities: list[Capability],
) -> list[DeviceCapability]:
    """Create device capability records for a device.

    Args:
        device_id: The device ID
        capabilities: List of capabilities to assign to the device

    Returns:
        List of DeviceCapability objects created
    """
    device_capabilities: list[DeviceCapability] = []
    now = datetime.now(UTC)

    for capability in capabilities:
        if not capability.id:
            logger.error(f"Capability {capability.code} has no ID, skipping")
            continue

        device_cap = DeviceCapability(
            id=None,
            device_id=device_id,
            capability_id=capability.id,
            created_at=now,
        )
        device_capabilities.append(device_cap)

    logger.info(f"Created {len(device_capabilities)} device capabilities for device {device_id}")
    return device_capabilities
