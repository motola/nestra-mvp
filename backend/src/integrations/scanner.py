"""
Universal local network scanner.

Concurrently discovers smart devices from all supported vendors:
  - Shelly  : HTTP GET /shelly on every IP in the local /24 subnet
  - Govee   : UDP broadcast on port 4001
  - LIFX    : UDP broadcast on port 56700 (standard LAN protocol)
  - Kasa    : UDP broadcast on port 9999 (XOR-encrypted payload)
  - Matter  : mDNS service discovery (_matter._tcp.local.) via zeroconf

Auto-detects local subnet. Hard timeout: 10 seconds total.
UDP scans run via asyncio.to_thread to avoid blocking the event loop.
"""

from __future__ import annotations

import asyncio
import ipaddress
import json
import logging
import socket
import struct
import time
from typing import Any

import httpx

from integrations.provisioning import get_local_subnet

logger = logging.getLogger(__name__)

_SCAN_TIMEOUT = 10.0
_HTTP_TIMEOUT = 0.3
_UDP_TIMEOUT = 3.0


# ── Shelly HTTP scan ──────────────────────────────────────────────────────────


async def scan_shelly(subnet: str) -> list[dict[str, Any]]:
    """GET /shelly on every host in the /24 subnet using one shared client."""
    hosts = list(ipaddress.IPv4Network(f"{subnet}/24", strict=False).hosts())
    sem = asyncio.Semaphore(200)

    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:

        async def check(ip: str) -> dict[str, Any] | None:
            async with sem:
                try:
                    r = await client.get(f"http://{ip}/shelly")
                    if r.status_code == 200:
                        data = r.json()
                        if "type" in data or "app" in data:
                            return {
                                "vendor": "shelly",
                                "name": data.get("name", data.get("app", f"Shelly@{ip}")),
                                "model": data.get("type", data.get("app", "Unknown")),
                                "ip": ip,
                                "mac": data.get("mac", ""),
                                "raw": data,
                            }
                except Exception:
                    pass
                return None

        results = await asyncio.gather(*[check(str(ip)) for ip in hosts])

    return [r for r in results if r is not None]


# ── Govee UDP scan ────────────────────────────────────────────────────────────

_GOVEE_PORT = 4001
_GOVEE_PACKET = json.dumps({"msg": {"cmd": "scan", "data": {"account_topic": "reserve"}}}).encode()


def _scan_govee_sync() -> list[dict[str, Any]]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(_UDP_TIMEOUT)
    devices: list[dict[str, Any]] = []
    try:
        sock.sendto(_GOVEE_PACKET, ("255.255.255.255", _GOVEE_PORT))
        deadline = time.monotonic() + _UDP_TIMEOUT
        while time.monotonic() < deadline:
            try:
                data, addr = sock.recvfrom(4096)
                payload = json.loads(data.decode())
                device_data = payload.get("msg", {}).get("data", {})
                devices.append(
                    {
                        "vendor": "govee",
                        "name": device_data.get("sku", f"Govee@{addr[0]}"),
                        "model": device_data.get("sku", "Unknown"),
                        "ip": addr[0],
                        "mac": device_data.get("device", ""),
                        "raw": payload,
                    }
                )
            except (TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
                break
    except Exception as exc:
        logger.debug("Govee UDP scan error: %s", exc)
    finally:
        sock.close()
    return devices


async def scan_govee() -> list[dict[str, Any]]:
    return await asyncio.to_thread(_scan_govee_sync)


# ── LIFX UDP scan ─────────────────────────────────────────────────────────────

_LIFX_PORT = 56700


def _build_lifx_packet() -> bytes:
    # LIFX LAN protocol — GetService (type=2), 36 bytes total
    # Frame: size(2) + protocol_word(2) + source(4)
    # protocol_word: protocol=1024 | addressable(bit12) | tagged(bit13) = 0x3400
    frame = struct.pack("<HHI", 36, 0x3400, 0)
    # Frame Address: target(8) + reserved(6) + flags(1) + sequence(1)
    frame_addr = struct.pack("<8s6sBB", b"\x00" * 8, b"\x00" * 6, 0, 0)
    # Protocol Header: reserved(8) + type(2) + reserved(2)
    proto_hdr = struct.pack("<QHH", 0, 2, 0)
    return frame + frame_addr + proto_hdr


def _scan_lifx_sync() -> list[dict[str, Any]]:
    packet = _build_lifx_packet()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(_UDP_TIMEOUT)
    devices: list[dict[str, Any]] = []
    try:
        sock.sendto(packet, ("255.255.255.255", _LIFX_PORT))
        deadline = time.monotonic() + _UDP_TIMEOUT
        while time.monotonic() < deadline:
            try:
                data, addr = sock.recvfrom(128)
                devices.append(
                    {
                        "vendor": "lifx",
                        "name": f"LIFX@{addr[0]}",
                        "model": "LIFX Light",
                        "ip": addr[0],
                        "mac": "",
                        "raw": {"bytes": data.hex()},
                    }
                )
            except TimeoutError:
                break
    except Exception as exc:
        logger.debug("LIFX UDP scan error: %s", exc)
    finally:
        sock.close()
    return devices


async def scan_lifx() -> list[dict[str, Any]]:
    return await asyncio.to_thread(_scan_lifx_sync)


# ── TP-Link Kasa UDP scan ─────────────────────────────────────────────────────

_KASA_PORT = 9999


def _kasa_encrypt(text: str) -> bytes:
    key = 171
    out = bytearray()
    for char in text.encode():
        key ^= char
        out.append(key)
    return bytes(out)


def _kasa_decrypt(data: bytes) -> str:
    key = 171
    out: list[str] = []
    for byte in data:
        out.append(chr(key ^ byte))
        key = byte
    return "".join(out)


_KASA_PACKET = _kasa_encrypt('{"system":{"get_sysinfo":{}}}')


def _scan_kasa_sync() -> list[dict[str, Any]]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(_UDP_TIMEOUT)
    devices: list[dict[str, Any]] = []
    try:
        sock.sendto(_KASA_PACKET, ("255.255.255.255", _KASA_PORT))
        deadline = time.monotonic() + _UDP_TIMEOUT
        while time.monotonic() < deadline:
            try:
                data, addr = sock.recvfrom(4096)
                payload = json.loads(_kasa_decrypt(data))
                info = payload.get("system", {}).get("get_sysinfo", {})
                devices.append(
                    {
                        "vendor": "kasa",
                        "name": info.get("alias", f"Kasa@{addr[0]}"),
                        "model": info.get("model", "Unknown"),
                        "ip": addr[0],
                        "mac": info.get("mac", ""),
                        "raw": info,
                    }
                )
            except (TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
                break
    except Exception as exc:
        logger.debug("Kasa UDP scan error: %s", exc)
    finally:
        sock.close()
    return devices


async def scan_kasa() -> list[dict[str, Any]]:
    return await asyncio.to_thread(_scan_kasa_sync)


# ── Matter mDNS scan ──────────────────────────────────────────────────────────

_MATTER_SERVICE = "_matterd._udp.local."
_MATTER_BROWSE_TIMEOUT = 30.0


def _scan_matter_sync() -> list[dict[str, Any]]:
    """Browse for _matter._tcp.local. services using zeroconf."""
    try:
        from zeroconf import ServiceBrowser, Zeroconf
    except ImportError:
        logger.debug("zeroconf not available — skipping Matter mDNS scan")
        return []

    devices: list[dict[str, Any]] = []

    class _Handler:
        def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            info = zc.get_service_info(type_, name)
            if info:
                addresses = [socket.inet_ntoa(a) for a in info.addresses if len(a) == 4]
                ip = addresses[0] if addresses else ""
                devices.append(
                    {
                        "vendor": "matter",
                        "name": name.replace(f".{type_}", "").replace("._matter._tcp.local.", ""),
                        "model": "Matter Device",
                        "ip": ip,
                        "mac": "",
                        "raw": {"service": name, "port": info.port},
                    }
                )

        def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            pass

        def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            pass

    zc = Zeroconf()
    try:
        ServiceBrowser(zc, _MATTER_SERVICE, _Handler())
        import time

        time.sleep(_MATTER_BROWSE_TIMEOUT)
    finally:
        zc.close()

    return devices


async def scan_matter() -> list[dict[str, Any]]:
    return await asyncio.to_thread(_scan_matter_sync)


# ── Combined scan ─────────────────────────────────────────────────────────────


async def scan_all() -> list[dict[str, Any]]:
    """Scan the local /24 subnet for Shelly devices."""
    subnet = get_local_subnet()
    logger.info("Scanning subnet %s/24", subnet)
    try:
        devices = await asyncio.wait_for(scan_shelly(subnet), timeout=_SCAN_TIMEOUT)
    except TimeoutError:
        logger.warning("Network scan timed out after %ss", _SCAN_TIMEOUT)
        return []
    devices.sort(key=lambda d: d.get("name", ""))
    logger.info("Scan complete — found %d device(s)", len(devices))
    return devices
