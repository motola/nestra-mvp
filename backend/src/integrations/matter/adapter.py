"""Matter integration — commissioning via python-matter-server WebSocket."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

from websockets.asyncio.client import connect

from spire import SpireDevice, VendorAdapter

logger = logging.getLogger(__name__)

_MATTER_WS_URL = "ws://localhost:5580/ws"
_TIMEOUT = 60.0
_DEFAULT_TIMEOUT = 120.0

# Level-control transition options shared by dimming/colour commands.
_LEVEL_OPTS = {"TransitionTime": 0, "OptionsMask": 0, "OptionsOverride": 0}


class MatterAdapter(VendorAdapter):
    """Lists, reads, and controls commissioned Matter nodes via python-matter-server."""

    async def list_devices(self) -> list[SpireDevice]:
        try:
            async with MatterServerClient() as client:
                nodes = await client.get_nodes()
            return [normalise_node(node) for node in nodes]
        except Exception as exc:
            logger.error("Matter list_devices failed: %s", exc)
            return []

    async def get_device_state(self, device_id: str) -> SpireDevice:
        async with MatterServerClient() as client:
            node = await client.get_node(device_id)
        if not node:
            raise RuntimeError(f"Matter node {device_id} not found")
        return normalise_node(node)

    async def send_command(self, device_id: str, command: dict[str, Any]) -> bool:
        spec = _matter_cluster_command(command.get("action", ""), command.get("value"))
        if spec is None:
            return False
        cluster_id, command_name, payload = spec
        async with MatterServerClient() as client:
            await client.send_command(device_id, 1, cluster_id, command_name, payload)
        return True


def _matter_cluster_command(action: str, value: Any) -> tuple[int, str, dict[str, Any]] | None:
    """Map a canonical SPIRE command to a Matter (cluster_id, command_name, payload)."""
    if action == "turn_on":
        return (6, "on", {})
    if action == "turn_off":
        return (6, "off", {})
    if action == "set_brightness":  # SPIRE brightness is 0-100; Matter Level is 0-254.
        return (8, "move_to_level", {"Level": round(int(value) * 2.54), **_LEVEL_OPTS})
    if action == "set_color_temp":
        payload = {"ColorTemperatureMireds": int(value), **_LEVEL_OPTS}
        return (768, "move_to_color_temperature", payload)
    if action == "lock":
        return (257, "lock_door", {})
    if action == "unlock":
        return (257, "unlock_door", {})
    return None


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
    """Convert a python-matter-server node dict into a SpireDevice with live state."""
    node_id = str(node.get("node_id", uuid.uuid4()))
    name = _extract_name(node) or f"Matter Device {node_id}"
    device_type = _infer_type(node)
    attrs = node.get("attributes", {})

    state: dict[str, Any] = {"node_id": node_id}
    commands: list[str] = []

    on_off = _read_attr(attrs, "6", "OnOff")
    if on_off is not None:
        state["on"] = bool(on_off)
        commands += ["turn_on", "turn_off"]
    level = _read_attr(attrs, "8", "CurrentLevel")
    if level is not None:
        state["brightness"] = round(int(level) / 2.54)  # Matter 0-254 -> SPIRE percent
        commands.append("set_brightness")
    if device_type == "lock":
        commands += ["lock", "unlock"]

    device = SpireDevice.from_vendor(
        vendor="matter",
        vendor_id=node_id,
        name=name,
        device_type=device_type,
        online=node.get("available", True),
        state=state,
        supported_commands=commands,
    )
    device.placement.property_id = property_id or None
    device.placement.room_id = room_id or None
    return device


def _read_attr(attrs: Any, cluster: str, name: str) -> Any:
    """Read a Matter cluster attribute, trying endpoint 1 then 0, name then index 0."""
    if not isinstance(attrs, dict):
        return None
    for endpoint in ("1", "0"):
        cluster_attrs = attrs.get(endpoint, {}).get(cluster, {})
        if cluster_attrs:
            return cluster_attrs.get(name, cluster_attrs.get("0"))
    return None


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


class MatterServerClient:
    """Async context manager wrapping the python-matter-server WebSocket API."""

    def __init__(self, url: str = _MATTER_WS_URL) -> None:
        self._url = url
        self._ws: Any = None
        self._cm: Any = None

    async def connect(self) -> None:
        self._cm = connect(self._url)
        self._ws = await self._cm.__aenter__()
        hello = await self._ws.recv()
        logger.debug("Matter server hello: %s", hello)

    async def commission_with_code(self, setup_code: str) -> dict[str, Any]:
        msg_id = f"commission-{uuid.uuid4().hex[:8]}"
        await self._ws.send(
            json.dumps(
                {
                    "message_id": msg_id,
                    "command": "commission_with_code",
                    "args": {"code": setup_code, "network_only": True},
                }
            )
        )
        return await self._wait(msg_id)

    async def get_nodes(self) -> list[dict[str, Any]]:
        msg_id = f"get-nodes-{uuid.uuid4().hex[:8]}"
        await self._ws.send(
            json.dumps(
                {
                    "message_id": msg_id,
                    "command": "get_nodes",
                    "args": {},
                }
            )
        )
        result = await self._wait(msg_id)
        return result.get("result") or []

    async def get_node(self, node_id: int | str) -> dict[str, Any] | None:
        nodes = await self.get_nodes()
        for node in nodes:
            if str(node.get("node_id")) == str(node_id):
                return node
        return None

    async def send_command(
        self,
        node_id: int | str,
        endpoint_id: int,
        cluster_id: int,
        command: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        msg_id = f"cmd-{uuid.uuid4().hex[:8]}"
        await self._ws.send(
            json.dumps(
                {
                    "message_id": msg_id,
                    "command": "device_command",
                    "args": {
                        "node_id": int(node_id),
                        "endpoint_id": endpoint_id,
                        "cluster_id": cluster_id,
                        "command_name": command,
                        "payload": payload or {},
                    },
                }
            )
        )
        return await self._wait(msg_id)

    async def close(self) -> None:
        if self._cm:
            await self._cm.__aexit__(None, None, None)
            self._ws = None
            self._cm = None

    async def _wait(self, message_id: str, timeout: float = _DEFAULT_TIMEOUT) -> dict[str, Any]:
        loop = asyncio.get_event_loop()
        deadline = loop.time() + timeout
        while True:
            remaining = deadline - loop.time()
            if remaining <= 0:
                raise TimeoutError(f"Timed out waiting for Matter server response to {message_id}")
            raw = await asyncio.wait_for(self._ws.recv(), timeout=remaining)
            msg: dict[str, Any] = json.loads(raw)
            if msg.get("message_id") == message_id:
                return msg

    async def __aenter__(self) -> MatterServerClient:
        await self.connect()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
