from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from demo import govee, lifx

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
    except httpx.HTTPStatusError:
        pass

    try:
        govee_devices = await govee.list_devices()
        devices.extend(_govee_to_device(d) for d in govee_devices)
    except httpx.HTTPStatusError:
        pass

    return devices


@router.post("/devices/{provider}/{device_id}/power", response_model=dict[str, object])
async def set_power(provider: str, device_id: str, body: PowerBody) -> dict[str, object]:
    """Turn a device on or off."""
    try:
        if provider == "lifx":
            return await lifx.set_power(device_id, "on" if body.on else "off")
        if provider == "govee":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Govee power requires model — use /demo/devices/govee/{id}/power-with-model",
            )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Device provider returned an error.",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unknown provider: {provider}",
    )


@router.post("/devices/govee/{device_id}/power", response_model=dict[str, object])
async def set_govee_power(device_id: str, body: PowerBody, model: str) -> dict[str, object]:
    """Turn a Govee device on or off (model required as query param)."""
    try:
        return await govee.set_power(device_id, model, on=body.on)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Device provider returned an error.",
        ) from exc


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
