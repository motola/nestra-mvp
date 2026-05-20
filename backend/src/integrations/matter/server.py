"""Reusable WebSocket client for python-matter-server."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

from websockets.asyncio.client import connect

logger = logging.getLogger(__name__)

_MATTER_WS_URL = "ws://localhost:5580/ws"
_DEFAULT_TIMEOUT = 120.0


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
