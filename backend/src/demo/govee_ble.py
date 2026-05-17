from __future__ import annotations

import time

from bleak import BleakClient, BleakScanner

from config import get_settings

_WRITE_CHAR = "00010203-0405-0607-0809-0a0b0c0d2b11"
_SCAN_TIMEOUT = 5.0
_CACHE_TTL = 30.0

_cache: list[dict[str, object]] = []
_cache_time: float = 0.0
_power_state: dict[str, bool] = {}


def _packet(cmd: int, data: list[int]) -> bytes:
    payload = [0x33, cmd] + data
    payload += [0x00] * (19 - len(payload))
    xor = 0
    for b in payload:
        xor ^= b
    payload.append(xor)
    return bytes(payload)


async def list_devices() -> list[dict[str, object]]:
    global _cache, _cache_time

    address = get_settings().govee_ble_address
    if address:
        return [
            {
                "device": address,
                "deviceName": "Govee H617C",
                "model": "ble",
                "controllable": True,
                "_power": _power_state.get(address, False),
            }
        ]

    if time.monotonic() - _cache_time < _CACHE_TTL:
        return _cache

    found = await BleakScanner.discover(timeout=_SCAN_TIMEOUT)
    _cache = [
        {
            "device": d.address,
            "deviceName": d.name or "Govee H617C",
            "model": "ble",
            "controllable": True,
            "_power": _power_state.get(d.address, False),
        }
        for d in found
        if d.name and "H617C" in d.name
    ]
    _cache_time = time.monotonic()
    return _cache


async def set_power(address: str, *, on: bool) -> None:
    packet = _packet(0x01, [0x01 if on else 0x00])
    device = await BleakScanner.find_device_by_address(address, timeout=10.0)
    if device is None:
        raise RuntimeError(f"BLE device {address} not found nearby")
    async with BleakClient(device) as client:
        await client.write_gatt_char(_WRITE_CHAR, packet, response=True)
    _power_state[address] = on
