"""Claude tool definitions for device control."""

from __future__ import annotations

DEVICE_TOOLS = [
    {
        "name": "list_devices",
        "description": "List all smart home devices in the property",
        "input_schema": {
            "type": "object",
            "properties": {
                "property_id": {
                    "type": "string",
                    "description": "UUID of the property to list devices for",
                }
            },
            "required": ["property_id"],
        },
    },
    {
        "name": "control_lock",
        "description": "Lock or unlock a smart lock device",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "UUID of the lock device",
                },
                "action": {
                    "type": "string",
                    "enum": ["lock", "unlock"],
                    "description": "Action to perform on the lock",
                },
            },
            "required": ["device_id", "action"],
        },
    },
    {
        "name": "set_temperature",
        "description": "Set the target temperature on a smart thermostat",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "UUID of the thermostat device",
                },
                "temperature": {
                    "type": "number",
                    "description": "Target temperature in Celsius",
                },
            },
            "required": ["device_id", "temperature"],
        },
    },
    {
        "name": "toggle_plug",
        "description": "Turn a smart plug on or off",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "UUID of the plug device",
                },
                "power_state": {
                    "type": "boolean",
                    "description": "True to turn on, False to turn off",
                },
            },
            "required": ["device_id", "power_state"],
        },
    },
    {
        "name": "get_device_status",
        "description": "Get current status and readings of a specific device",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "UUID of the device",
                }
            },
            "required": ["device_id"],
        },
    },
]
