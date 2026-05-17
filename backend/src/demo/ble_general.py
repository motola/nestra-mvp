from __future__ import annotations

from dataclasses import dataclass, field

from bleak import BleakClient, BleakScanner

_SCAN_TIMEOUT = 8.0
_PROBE_TIMEOUT = 10.0
_RSSI_FLOOR = -90

_TYPE_PATTERNS: dict[str, list[str]] = {
    "light": ["govee", "ihoment", "lifx", "hue", "sengled", "wyze", "cree", "wiz"],
    "speaker": [
        "jbl",
        "sony",
        "bose",
        "airpods",
        "marshall",
        "harman",
        "beats",
        "jabra",
        "sennheiser",
        "anker",
        "soundcore",
        "ultimate ears",
        "ue boom",
        "sonos",
        "bang",
        "olufsen",
    ],
    "phone": ["iphone", "samsung", "pixel", "oneplus", "xiaomi", "huawei", "galaxy"],
}


def detect_type(name: str | None) -> str:
    if not name:
        return "unknown"
    lower = name.lower()
    for device_type, patterns in _TYPE_PATTERNS.items():
        if any(p in lower for p in patterns):
            return device_type
    return "unknown"


@dataclass
class ScannedDevice:
    address: str
    name: str
    device_type: str
    rssi: int | None = None


@dataclass
class ProbeResult:
    address: str
    name: str
    device_type: str
    connectable: bool
    services: list[dict[str, object]] = field(default_factory=list)
    error: str | None = None


async def scan() -> list[ScannedDevice]:
    found = await BleakScanner.discover(timeout=_SCAN_TIMEOUT)
    devices = [
        ScannedDevice(
            address=d.address,
            name=d.name or "Unknown device",
            device_type=detect_type(d.name),
            rssi=d.rssi,
        )
        for d in found
        if d.name and (d.rssi is None or d.rssi >= _RSSI_FLOOR)
    ]
    devices.sort(key=lambda d: (d.device_type != "unknown", d.name.lower()))
    return devices


async def probe(address: str) -> ProbeResult:
    device = await BleakScanner.find_device_by_address(address, timeout=_PROBE_TIMEOUT)
    if device is None:
        return ProbeResult(
            address=address,
            name="Unknown",
            device_type="unknown",
            connectable=False,
            error="Device not found — it may be out of range or connected to another host.",
        )
    try:
        services: list[dict[str, object]] = []
        async with BleakClient(device) as client:
            for svc in client.services:
                services.append(
                    {
                        "uuid": svc.uuid,
                        "characteristics": [
                            {"uuid": c.uuid, "properties": list(c.properties)}
                            for c in svc.characteristics
                        ],
                    }
                )
        return ProbeResult(
            address=address,
            name=device.name or "Unknown",
            device_type=detect_type(device.name),
            connectable=True,
            services=services,
        )
    except Exception as exc:
        return ProbeResult(
            address=address,
            name=device.name or "Unknown",
            device_type=detect_type(device.name),
            connectable=False,
            error=str(exc),
        )
