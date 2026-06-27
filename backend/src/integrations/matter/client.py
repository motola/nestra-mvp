"""Matter integration — commissioning via python-matter-server WebSocket."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from websockets.asyncio.client import connect

from spire import SpireDevice, VendorAdapter

logger = logging.getLogger(__name__)

_MATTER_WS_URL = "ws://localhost:5580/ws"
_TIMEOUT = 60.0


class MatterAdapter(VendorAdapter):
    """Stub adapter for non-commission operations — full device control not yet implemented."""

    async def list_devices(self) -> list[SpireDevice]:
        return []

    async def get_device_state(self, device_id: str) -> SpireDevice:
        raise NotImplementedError

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        raise NotImplementedError


async def commission_device(setup_code: str) -> dict[str, Any]:
    """
    Connect to python-matter-server and commission a device using its setup code.
    Returns the raw node dict from the Matter server.
    """
    commission_id = f"commission-{uuid.uuid4().hex[:8]}"
    get_nodes_id = f"get-nodes-{uuid.uuid4().hex[:8]}"

    async with connect(_MATTER_WS_URL) as ws:
        # Wait for the server ready event before sending commands
        sdk_version_msg = await ws.recv()
        logger.debug("Matter server hello: %s", sdk_version_msg)

        # Send commission_with_code
        await ws.send(
            json.dumps(
                {
                    "message_id": commission_id,
                    "command": "commission_with_code",
                    "args": {
                        "code": setup_code,
                        "network_only": False,
                    },
                }
            )
        )

        # Wait for the commission response
        commission_result = await _wait_for_response(ws, commission_id)
        logger.info("Commission result: %s", commission_result)

        if commission_result.get("error_code"):
            raise RuntimeError(
                f"Matter commissioning failed: "
                f"{commission_result.get('details', commission_result)}"
            )

        # Retrieve commissioned node details
        await ws.send(
            json.dumps(
                {
                    "message_id": get_nodes_id,
                    "command": "get_nodes",
                    "args": {},
                }
            )
        )

        nodes_result = await _wait_for_response(ws, get_nodes_id)
        nodes: list[dict[str, Any]] = nodes_result.get("result", [])

        # Return the most recently commissioned node (last in list)
        if nodes:
            return nodes[-1]

        out: dict[str, Any] = commission_result.get("result", {})
        return out


async def _wait_for_response(ws: Any, message_id: str, timeout: float = _TIMEOUT) -> dict[str, Any]:
    """Read messages until we find the one matching message_id."""
    import asyncio

    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        remaining = deadline - asyncio.get_event_loop().time()
        if remaining <= 0:
            raise TimeoutError(f"Timed out waiting for Matter server response to {message_id}")
        raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
        msg: dict[str, Any] = json.loads(raw)
        if msg.get("message_id") == message_id:
            return msg


def normalise_node(node: dict[str, Any], property_id: str = "", room_id: str = "") -> SpireDevice:
    """Convert a python-matter-server node dict into a SpireDevice."""
    node_id = str(node.get("node_id", uuid.uuid4()))
    name = _extract_name(node) or f"Matter Device {node_id}"
    device_type = _infer_type(node)

    device = SpireDevice.from_vendor(
        vendor="matter",
        vendor_id=node_id,
        name=name,
        device_type=device_type,
        online=node.get("available", True),
        state={"node_id": node_id},
    )
    device.placement.property_id = property_id or None
    device.placement.room_id = room_id or None
    return device


def _extract_name(node: dict[str, Any]) -> str:
    """Pull a human-readable name from the node's attribute cache."""
    attrs = node.get("attributes", {})
    # Basic Information cluster (0x0028) NodeLabel attribute (0x0005)
    for endpoint_attrs in attrs.values() if isinstance(attrs, dict) else []:
        if isinstance(endpoint_attrs, dict):
            basic = endpoint_attrs.get("0", {})  # cluster 0 = Basic Information
            label = basic.get("NodeLabel") or basic.get("5")
            if label:
                return str(label)
    return ""


def _infer_type(node: dict[str, Any]) -> str:
    """Infer device type from Matter device type list."""
    device_types = node.get("device_type", [])
    if isinstance(device_types, list):
        for dt in device_types:
            dt_id = dt.get("device_type") if isinstance(dt, dict) else dt
            if dt_id in (0x0100, 0x010C, 0x010D):  # On/Off Light, Extended Color Light, Color Temp
                return "light"
            if dt_id in (0x010A, 0x010B):  # On/Off Plug, Dimmable Plug
                return "plug"
            if dt_id == 0x0302:  # Temperature Sensor
                return "sensor"
            if dt_id == 0x000A:  # Door Lock
                return "lock"
            if dt_id == 0x0301:  # Thermostat
                return "thermostat"
    return "light"
