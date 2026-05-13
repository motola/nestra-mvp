from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from demo import ble_general, govee, govee_ble, lifx

router = APIRouter(prefix="/demo", tags=["demo"])


class DemoDevice(BaseModel):
    id: str
    provider: str
    name: str
    power: bool
    brightness: float | None = None
    reachable: bool = True
    model: str | None = None


class PowerBody(BaseModel):
    on: bool


class BrightnessBody(BaseModel):
    brightness: float


def _lifx_to_device(raw: dict[str, object]) -> DemoDevice:
    return DemoDevice(
        id=str(raw["id"]),
        provider="lifx",
        name=str(raw.get("label", "LIFX Light")),
        power=str(raw.get("power", "off")) == "on",
        brightness=float(raw["brightness"]) if raw.get("brightness") is not None else None,  # type: ignore[arg-type]
        reachable=bool(raw.get("connected", True)),
    )


def _govee_to_device(raw: dict[str, object]) -> DemoDevice:
    return DemoDevice(
        id=str(raw["device"]),
        provider="govee",
        name=str(raw.get("deviceName", "Govee Device")),
        power=bool(raw.get("_power", False)),
        reachable=bool(raw.get("controllable", True)),
        model=str(raw.get("model", "")),
    )


@router.get("/devices", response_model=list[DemoDevice])
async def list_devices() -> list[DemoDevice]:
    """Return all LIFX and Govee devices merged into a single list."""
    devices: list[DemoDevice] = []

    try:
        lifx_lights = await lifx.list_lights()
        devices.extend(_lifx_to_device(light) for light in lifx_lights)
    except (httpx.HTTPStatusError, RuntimeError):
        pass

    try:
        govee_devices = await govee.list_devices()
        devices.extend(_govee_to_device(d) for d in govee_devices)
    except (httpx.HTTPStatusError, RuntimeError):
        pass

    try:
        ble_devices = await govee_ble.list_devices()
        devices.extend(_govee_to_device(d) for d in ble_devices)
    except Exception:
        pass

    return devices


@router.post("/devices/govee/{device_id}/power", response_model=dict[str, object])
async def set_govee_power(device_id: str, body: PowerBody, model: str) -> dict[str, object]:
    """Turn a Govee device on or off (model required as query param; model=ble routes to BLE)."""
    try:
        if model == "ble":
            await govee_ble.set_power(device_id, on=body.on)
            return {"status": "ok"}
        return await govee.set_power(device_id, model, on=body.on)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Device provider returned an error.",
        ) from exc


@router.post("/devices/{provider}/{device_id}/power", response_model=dict[str, object])
async def set_power(provider: str, device_id: str, body: PowerBody) -> dict[str, object]:
    """Turn a device on or off."""
    try:
        if provider == "lifx":
            return await lifx.set_power(device_id, "on" if body.on else "off")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Device provider returned an error.",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unknown provider: {provider}",
    )


@router.post("/devices/lifx/{device_id}/brightness", response_model=dict[str, object])
async def set_lifx_brightness(device_id: str, body: BrightnessBody) -> dict[str, object]:
    """Set LIFX light brightness (0.0–1.0)."""
    try:
        return await lifx.set_brightness(device_id, body.brightness)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Device provider returned an error.",
        ) from exc


# ── BLE scanner ────────────────────────────────────────────────────────────────


class BLEScannedDevice(BaseModel):
    address: str
    name: str
    device_type: str


class BLEProbeResult(BaseModel):
    address: str
    name: str
    device_type: str
    connectable: bool
    services: list[dict[str, object]] = []
    error: str | None = None


@router.get("/ble/scan", response_model=list[BLEScannedDevice])
async def ble_scan() -> list[BLEScannedDevice]:
    """Scan for all nearby BLE devices and classify by type."""
    try:
        devices = await ble_general.scan()
        return [
            BLEScannedDevice(address=d.address, name=d.name, device_type=d.device_type)
            for d in devices
        ]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"BLE scan failed: {exc}",
        ) from exc


@router.post("/ble/{address}/probe", response_model=BLEProbeResult)
async def ble_probe(address: str) -> BLEProbeResult:
    """Connect to a BLE device and return its services and capabilities."""
    result = await ble_general.probe(address)
    return BLEProbeResult(
        address=result.address,
        name=result.name,
        device_type=result.device_type,
        connectable=result.connectable,
        services=result.services,  # type: ignore[arg-type]
        error=result.error,
    )
