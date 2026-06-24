"""
Shelly device provisioning — Windows WiFi flow.

Steps:
  1. Scan for Shelly device APs via netsh wlan show networks
  2. Connect laptop to the Shelly AP
  3. POST home WiFi credentials to the device at 192.168.33.1
  4. Reboot device, reconnect laptop to home network
  5. Scan local /24 subnet for the newly joined device

All netsh commands run via asyncio.to_thread (non-blocking subprocess).
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import re
import subprocess
import tempfile
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_SHELLY_AP_IP = "192.168.33.1"
_HOTSPOT_WAIT = 8  # seconds after connecting to Shelly AP before HTTP is ready
_REBOOT_WAIT = 12  # seconds for device to reboot and join home network


async def scan_shelly_hotspots() -> list[str]:
    """Return SSIDs of nearby Shelly device APs found by netsh."""
    result = await asyncio.to_thread(
        subprocess.run,
        ["netsh", "wlan", "show", "networks", "mode=bssid"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    ssids: list[str] = []
    for line in result.stdout.splitlines():
        m = re.match(r"^SSID\s+\d+\s*:\s*(.+)$", line.strip())
        if m:
            ssid = m.group(1).strip()
            if ssid.upper().startswith("SHELLY"):
                ssids.append(ssid)
    return ssids


_OPEN_PROFILE_XML = """<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
  <name>{ssid}</name>
  <SSIDConfig><SSID><name>{ssid}</name></SSID></SSIDConfig>
  <connectionType>ESS</connectionType>
  <connectionMode>manual</connectionMode>
  <MSM>
    <security>
      <authEncryption>
        <authentication>open</authentication>
        <encryption>none</encryption>
        <useOneX>false</useOneX>
      </authEncryption>
    </security>
  </MSM>
</WLANProfile>"""


async def _add_open_profile(ssid: str) -> None:
    """Register a temporary open-network profile so Windows can join the Shelly AP.

    netsh cannot connect to a brand-new open SSID without a profile, which is why
    provisioning previously timed out trying to reach the device at 192.168.33.1.
    """
    fd, path = tempfile.mkstemp(suffix=".xml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(_OPEN_PROFILE_XML.format(ssid=ssid))
        await asyncio.to_thread(
            subprocess.run,
            ["netsh", "wlan", "add", "profile", f"filename={path}", "user=current"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    finally:
        with contextlib.suppress(OSError):
            os.remove(path)


async def scan_wifi_networks() -> list[str]:
    """Return SSIDs of nearby Wi-Fi networks for the home-network picker.

    Excludes the Shelly setup APs themselves. Scanned from the laptop, which is
    co-located with the device in AP mode, so it sees the same networks.
    """
    result = await asyncio.to_thread(
        subprocess.run,
        ["netsh", "wlan", "show", "networks"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    ssids: list[str] = []
    for line in result.stdout.splitlines():
        m = re.match(r"^SSID\s+\d+\s*:\s*(.+)$", line.strip())
        if m:
            ssid = m.group(1).strip()
            if ssid and not ssid.upper().startswith("SHELLY") and ssid not in ssids:
                ssids.append(ssid)
    return ssids


async def connect_hotspot(ssid: str) -> None:
    """Connect the Windows machine to the Shelly device AP and wait for link."""
    await _add_open_profile(ssid)
    await asyncio.to_thread(
        subprocess.run,
        ["netsh", "wlan", "connect", f"name={ssid}", f"ssid={ssid}"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    await asyncio.sleep(_HOTSPOT_WAIT)


async def send_wifi_credentials(home_ssid: str, home_password: str) -> None:
    """POST home WiFi credentials to Shelly device at 192.168.33.1, then reboot."""
    payload = {
        "config": {
            "sta": {
                "ssid": home_ssid,
                "pass": home_password,
                "enable": True,
            }
        }
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(f"http://{_SHELLY_AP_IP}/rpc/WiFi.SetConfig", json=payload)
        await client.post(f"http://{_SHELLY_AP_IP}/rpc/Shelly.Reboot")


async def reconnect_home(home_ssid: str) -> None:
    """Reconnect laptop to home network and wait for device reboot."""
    await asyncio.to_thread(
        subprocess.run,
        ["netsh", "wlan", "connect", f"name={home_ssid}"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    await asyncio.sleep(_REBOOT_WAIT)


def get_local_subnet() -> str:
    """
    Find the real WiFi subnet by looking for the adapter
    that has a Default Gateway — that's always the internet-
    connected network, not VMware or virtual adapters.
    """
    import re
    import subprocess

    result = subprocess.run(["ipconfig"], capture_output=True, text=True)

    current_ip = None
    for line in result.stdout.split("\n"):
        # Store the IP when we see it
        ip_match = re.search(r"IPv4 Address.*?:\s*([\d.]+)", line)
        if ip_match:
            current_ip = ip_match.group(1)

        # When we see a real gateway, the current_ip is our answer
        gateway_match = re.search(r"Default Gateway.*?:\s*([\d.]+)", line)
        if gateway_match and current_ip:
            prefix, _ = current_ip.rsplit(".", 1)
            return f"{prefix}.0"

    return "192.168.1.0"


async def scan_for_device(subnet: str) -> dict[str, Any] | None:
    """
    Scan the /24 subnet for a Shelly device responding on GET /shelly.
    Returns first found device dict or None.
    """
    import ipaddress

    hosts = list(ipaddress.IPv4Network(f"{subnet}/24", strict=False).hosts())
    sem = asyncio.Semaphore(40)

    async def check(ip: str) -> dict[str, Any] | None:
        async with sem:
            try:
                async with httpx.AsyncClient(timeout=1.5) as client:
                    r = await client.get(f"http://{ip}/shelly")
                    if r.status_code == 200:
                        data = r.json()
                        if "type" in data or "app" in data:
                            return {
                                "vendor": "shelly",
                                "name": data.get("name", data.get("app", f"Shelly@{ip}")),
                                "model": data.get("type", data.get("app", "Unknown")),
                                "mac": data.get("mac", ""),
                                "ip": ip,
                                "raw": data,
                            }
            except Exception:
                pass
            return None

    results = await asyncio.gather(*[check(str(ip)) for ip in hosts])
    found = [r for r in results if r is not None]
    return found[0] if found else None
