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


def _force_wifi_scan() -> None:
    """Trigger a fresh Windows Wi-Fi scan via the native WlanScan API.

    `netsh wlan show networks` only reports Windows' last cached scan, so without
    this the Rescan button just re-reads stale results. WlanScan asks the radio
    to scan now; results land a couple of seconds later. Best-effort.
    """
    try:
        import ctypes
        from ctypes import POINTER, Structure, byref, c_ubyte, wintypes

        class GUID(Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", c_ubyte * 8),
            ]

        class WLAN_INTERFACE_INFO(Structure):
            _fields_ = [
                ("InterfaceGuid", GUID),
                ("strInterfaceDescription", wintypes.WCHAR * 256),
                ("isState", wintypes.DWORD),
            ]

        class WLAN_INTERFACE_INFO_LIST(Structure):
            _fields_ = [
                ("dwNumberOfItems", wintypes.DWORD),
                ("dwIndex", wintypes.DWORD),
                ("InterfaceInfo", WLAN_INTERFACE_INFO * 8),
            ]

        wlan = ctypes.windll.wlanapi
        handle = wintypes.HANDLE()
        version = wintypes.DWORD()
        if wlan.WlanOpenHandle(2, None, byref(version), byref(handle)) != 0:
            return
        try:
            ptr = POINTER(WLAN_INTERFACE_INFO_LIST)()
            if wlan.WlanEnumInterfaces(handle, None, byref(ptr)) != 0:
                return
            info = ptr.contents
            for i in range(min(info.dwNumberOfItems, 8)):
                guid = info.InterfaceInfo[i].InterfaceGuid
                wlan.WlanScan(handle, byref(guid), None, None, None)
            wlan.WlanFreeMemory(ptr)
        finally:
            wlan.WlanCloseHandle(handle, None)
    except Exception as exc:
        logger.warning("WlanScan force-scan failed: %s", exc)


async def scan_shelly_hotspots() -> list[str]:
    """Force a fresh Wi-Fi scan, then return nearby Shelly device APs."""
    await asyncio.to_thread(_force_wifi_scan)
    await asyncio.sleep(2.5)  # let the radio finish the scan before reading
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


def _current_ssid() -> str | None:
    """The SSID the laptop is currently on (to restore it after a device scan)."""
    result = subprocess.run(
        ["netsh", "wlan", "show", "interfaces"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    for line in result.stdout.splitlines():
        m = re.match(r"^\s*SSID\s*:\s*(.+)$", line)
        if m:
            return m.group(1).strip()
    return None


async def scan_networks_via_shelly(hotspot_ssid: str) -> list[dict[str, Any]]:
    """Ask the Shelly itself which Wi-Fi networks it can see (RPC WiFi.Scan).

    The device's own radio is what must reach the home network, so its scan is
    more reliable than the laptop's. Connects to the Shelly AP, scans, then
    restores the laptop to whatever network it was on.
    """
    home = await asyncio.to_thread(_current_ssid)
    await connect_hotspot(hotspot_ssid)
    networks: list[dict[str, Any]] = []
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            seen: set[str] = set()
            # A single Wi-Fi scan misses networks, so sweep several times and
            # merge unique SSIDs — that's why the list looked incomplete before.
            for attempt in range(3):
                try:
                    r = await client.get(f"http://{_SHELLY_AP_IP}/rpc/WiFi.Scan")
                    r.raise_for_status()
                    for ap in r.json().get("results", []):
                        ssid = ap.get("ssid")
                        if ssid and ssid not in seen:
                            seen.add(ssid)
                            networks.append(
                                {
                                    "ssid": ssid,
                                    "rssi": ap.get("rssi"),
                                    "open": ap.get("auth", 1) == 0,
                                }
                            )
                except Exception as exc:
                    logger.warning("Shelly WiFi.Scan pass %d failed: %s", attempt, exc)
                if attempt < 2:
                    await asyncio.sleep(2)
    except Exception as exc:
        logger.warning("Shelly WiFi.Scan failed: %s", exc)
    finally:
        if home:
            await asyncio.to_thread(
                subprocess.run,
                ["netsh", "wlan", "connect", f"name={home}"],
                capture_output=True,
                text=True,
                timeout=15,
            )
    networks.sort(key=lambda n: n.get("rssi") or -999, reverse=True)
    return networks


async def send_wifi_credentials(home_ssid: str, home_password: str) -> None:
    """Set the Shelly's home WiFi (STA) credentials over its own AP.

    The device joins the home network while keeping its AP up, so we can keep
    talking to it at 192.168.33.1 and ask it which IP it got. No reboot — that
    drops the AP (and is why the old Shelly.Reboot call returned 400).
    """
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
        r = await client.post(f"http://{_SHELLY_AP_IP}/rpc/WiFi.SetConfig", json=payload)
        r.raise_for_status()


async def get_device_info() -> dict[str, Any]:
    """Read the Shelly's identity (id, mac, model) over its AP. Tolerant: returns
    an empty dict if the device doesn't answer."""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(f"http://{_SHELLY_AP_IP}/rpc/Shelly.GetDeviceInfo")
            r.raise_for_status()
            return dict(r.json())
    except Exception as exc:
        logger.warning("Shelly.GetDeviceInfo failed: %s", exc)
        return {}


async def wait_for_sta_ip(attempts: int = 12, gap: float = 3.0) -> str | None:
    """Poll the Shelly (over its AP) until it reports the IP it got on the home
    network. The device knows its own STA IP, so there is no need to scan the
    home LAN for it.
    """
    async with httpx.AsyncClient(timeout=8.0) as client:
        for _ in range(attempts):
            try:
                r = await client.get(f"http://{_SHELLY_AP_IP}/rpc/WiFi.GetStatus")
                if r.status_code == 200:
                    data = r.json()
                    sta_ip = data.get("sta_ip")
                    if sta_ip and data.get("status") in ("got ip", "connected"):
                        return str(sta_ip)
            except Exception:
                pass
            await asyncio.sleep(gap)
    return None


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

    # The device can take 15–30s to reboot, join Wi-Fi and get a DHCP lease, so
    # scan several times rather than giving up after a single pass.
    for attempt in range(4):
        results = await asyncio.gather(*[check(str(ip)) for ip in hosts])
        found = [r for r in results if r is not None]
        if found:
            return found[0]
        if attempt < 3:
            await asyncio.sleep(8)
    return None
