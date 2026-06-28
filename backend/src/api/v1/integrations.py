"""Integration endpoints — vendor status, device provisioning, network scanning."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.dependencies import SessionDep, SettingsDep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])


# ── Pydantic request models ───────────────────────────────────────────────────


class ProvisionPayload(BaseModel):
    hotspot_name: str
    wifi_ssid: str
    wifi_password: str
    property_id: str = ""
    room_id: str = ""


class SaveDevicePayload(BaseModel):
    vendor: str
    name: str
    model: str = ""
    ip: str = ""
    mac: str = ""
    property_id: str = ""
    room_id: str | None = None
    vendor_id: str = ""


# ── Vendor status ─────────────────────────────────────────────────────────────


@router.get("/")
async def list_integrations(settings: SettingsDep) -> list[dict[str, Any]]:
    """Return connection status for all supported vendors, from the registry."""
    from integrations.registry import VENDOR_REGISTRY

    return [
        {
            "vendor": spec.name,
            "connected": spec.is_connected(settings),
            "display_name": spec.display_name,
            "description": spec.description,
        }
        for spec in VENDOR_REGISTRY
    ]


@router.post("/{vendor}/connect")
async def connect_vendor(
    vendor: str, payload: dict[str, Any], settings: SettingsDep
) -> dict[str, Any]:
    from integrations.registry import VENDOR_NAMES

    if vendor not in VENDOR_NAMES:
        raise HTTPException(status_code=400, detail=f"Unknown vendor: {vendor}")
    return {"vendor": vendor, "status": "connect_not_yet_implemented"}


# ── Discovery: Shelly hotspot scan ────────────────────────────────────────────


@router.get("/hotspots")
async def list_hotspots() -> list[str]:
    """Scan for nearby Shelly device access points using netsh (Windows)."""
    from integrations.shelly_local.provisioning import scan_shelly_hotspots

    return await scan_shelly_hotspots()


@router.get("/wifi-networks")
async def list_wifi_networks() -> list[str]:
    """Nearby Wi-Fi networks for the provisioning home-network picker."""
    from integrations.shelly_local.provisioning import scan_wifi_networks

    return await scan_wifi_networks()


class ShellyScanPayload(BaseModel):
    hotspot_name: str


@router.post("/shelly/scan")
async def shelly_scan(payload: ShellyScanPayload) -> list[dict[str, Any]]:
    """Connect to the Shelly AP and return the Wi-Fi networks the device itself sees."""
    from integrations.shelly_local.provisioning import scan_networks_via_shelly

    return await scan_networks_via_shelly(payload.hotspot_name)


# ── Discovery: Shelly provisioning (SSE stream) ───────────────────────────────


@router.post("/provision")
async def provision_device(payload: ProvisionPayload, settings: SettingsDep) -> StreamingResponse:
    """
    Run the full Shelly provisioning flow and stream live progress via SSE.

    SSE event format: data: {"type": "status"|"device"|"error"|"done", ...}
    WiFi credentials come from the request body and are never stored.
    """
    from integrations.shelly_local.provisioning import (
        connect_hotspot,
        get_device_info,
        reconnect_home,
        send_wifi_credentials,
        wait_for_sta_ip,
    )

    def sse(type_: str, **kwargs: object) -> str:
        return f"data: {json.dumps({'type': type_, **kwargs})}\n\n"

    async def stream() -> AsyncGenerator[str, None]:
        if not payload.wifi_ssid:
            yield sse("error", message="WiFi network name is required.")
            yield sse("done")
            return

        try:
            yield sse("status", message="Connecting to your device…")
            await connect_hotspot(payload.hotspot_name)

            yield sse("status", message="Reading the device…")
            info = await get_device_info()

            yield sse("status", message="Sending your Wi-Fi details…")
            await send_wifi_credentials(payload.wifi_ssid, payload.wifi_password)

            # The device keeps its AP up while joining home Wi-Fi, so we ask it
            # directly which IP it got rather than scanning the home network.
            yield sse("status", message="Waiting for the device to join your network…")
            sta_ip = await wait_for_sta_ip()

            yield sse("status", message="Reconnecting you to Wi-Fi…")
            await reconnect_home(payload.wifi_ssid)

            if sta_ip:
                device = {
                    "vendor": "shelly",
                    "name": info.get("name") or info.get("id") or "Shelly device",
                    "model": info.get("model") or info.get("app") or "Shelly",
                    "mac": info.get("mac", ""),
                    "ip": sta_ip,
                    "vendor_id": info.get("id", ""),
                }
                yield sse("status", message="Device ready!")
                yield sse("device", device=device)
            else:
                yield sse(
                    "error",
                    message=(
                        "The device didn't report joining your network — "
                        "double-check the Wi-Fi password and try again."
                    ),
                )
        except Exception as exc:
            logger.exception("Provisioning failed: %s", exc)
            yield sse("error", message=str(exc))
        finally:
            yield sse("done")

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Discovery: Universal network scan ────────────────────────────────────────


@router.get("/scan")
async def scan_network() -> list[dict[str, Any]]:
    """Scan the local network for all supported smart device vendors."""
    from integrations.scanner import scan_shelly
    from integrations.shelly_local.provisioning import get_local_subnet

    subnet = get_local_subnet()
    logger.debug("Scanning subnet %s", subnet)
    results = await scan_shelly(subnet)
    logger.debug("Found %d devices", len(results))
    return results


# ── Discovery: Matter scan ────────────────────────────────────────────────────


@router.get("/scan/matter")
async def scan_matter_devices() -> dict[str, Any]:
    from integrations.scanner import scan_matter

    devices = await scan_matter()
    return {"devices": devices}


# ── Discovery: Bluetooth (BLE) scan ───────────────────────────────────────────


@router.get("/scan/ble")
async def scan_ble_devices() -> list[dict[str, Any]]:
    """Scan for nearby Bluetooth (BLE) devices in range of this machine."""
    from integrations.scanner import scan_ble

    return await scan_ble()


# ── Matter: commission ────────────────────────────────────────────────────────


class MatterCommissionPayload(BaseModel):
    setup_code: str
    property_id: str = ""
    room_id: str = ""


@router.post("/matter/commission")
async def commission_matter_device(
    payload: MatterCommissionPayload, session: SessionDep
) -> StreamingResponse:
    """
    Commission a Matter device via python-matter-server, streaming SSE progress events.

    SSE event format: data: {"type": "status"|"device"|"error"|"done", ...}
    """
    from devices.registry import save_device as _save_device
    from integrations.matter.adapter import normalise_node
    from integrations.matter.server import MatterServerClient

    def sse(type_: str, **kwargs: object) -> str:
        return f"data: {json.dumps({'type': type_, **kwargs})}\n\n"

    async def stream() -> AsyncGenerator[str, None]:
        try:
            yield sse("status", message="Connecting to Matter server...")
            async with MatterServerClient() as client:
                yield sse("status", message="Commissioning device...")
                result = await client.commission_with_code(payload.setup_code)

                if result.get("error_code"):
                    yield sse("error", message=str(result.get("details", result)))
                    yield sse("done")
                    return

                yield sse("status", message="Device commissioned successfully!")
                nodes = await client.get_nodes()
                node = nodes[-1] if nodes else result.get("result", {})

            device = normalise_node(node, property_id=payload.property_id, room_id=payload.room_id)
            api = device.to_api()

            yield sse("status", message="Saving to your property...")
            try:
                saved = await _save_device(
                    {
                        "vendor": "matter",
                        "vendor_id": api["vendor_id"],
                        "name": api["name"],
                        "model": "Matter Device",
                        "ip": "",
                        "mac": "",
                        "property_id": payload.property_id,
                        "room_id": payload.room_id,
                    },
                    session,
                )
                device_id = saved.get("id", api["vendor_id"])
            except Exception as exc:
                logger.warning("Could not save Matter device: %s", exc)
                device_id = api["vendor_id"]

            yield sse("status", message="Done!")
            yield sse(
                "device",
                device={
                    "id": device_id,
                    "name": api["name"],
                    "vendor": "matter",
                    "vendor_id": api["vendor_id"],
                    "property_id": payload.property_id or None,
                    "room_id": payload.room_id or None,
                },
            )
        except TimeoutError as exc:
            yield sse("error", message=f"Timed out: {exc}")
        except Exception as exc:
            logger.exception("Matter commissioning error: %s", exc)
            yield sse("error", message=str(exc))
        finally:
            yield sse("done")

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Device registry ───────────────────────────────────────────────────────────


@router.get("/devices")
async def list_saved_devices(
    settings: SettingsDep,
    session: SessionDep,
    property_id: str | None = Query(default=None),
) -> list[dict[str, Any]]:
    """List all provisioned devices stored in the registry, optionally filtered by property."""
    from devices.registry import list_devices

    rows = await list_devices(session, property_id=property_id)
    if settings.demo_mode:
        from demo.data import DEMO_DEVICES, demo_device_as_saved

        demo_rows = [
            demo_device_as_saved(d)
            for d in DEMO_DEVICES
            if (property_id is None or d["property_id"] == property_id)
        ]
        return rows + demo_rows
    return rows


@router.post("/devices")
async def save_device(payload: SaveDevicePayload, session: SessionDep) -> dict[str, Any]:
    """Save a discovered device to the registry."""
    from devices.registry import save_device as _save

    try:
        return await _save(payload.model_dump(), session)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.patch("/devices/{device_id}")
async def rename_device(
    device_id: str, payload: dict[str, Any], session: SessionDep
) -> dict[str, Any]:
    """Update device fields (e.g. name) in the registry."""
    from devices.registry import update_device

    if not payload.get("name"):
        raise HTTPException(status_code=400, detail="name is required")
    try:
        return await update_device(device_id, {"name": payload["name"]}, session)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/devices/{device_id}")
async def remove_device(device_id: str, session: SessionDep) -> dict[str, Any]:
    """Remove a device from the registry by its ID."""
    from devices.registry import delete_device

    try:
        await delete_device(device_id, session)
        return {"deleted": device_id}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
