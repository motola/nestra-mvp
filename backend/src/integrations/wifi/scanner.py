"""WiFi network scanner service."""

from __future__ import annotations

import logging
import platform
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WiFiNetwork:
    """Represents a detected WiFi network."""

    ssid: str
    bssid: str
    signal_strength: int  # -30 to -90 dBm
    channel: int
    security: str  # open, wep, wpa, wpa2, wpa3


class WiFiScanner:
    """Scan for available WiFi networks on the system."""

    @staticmethod
    async def scan() -> list[WiFiNetwork]:
        """Scan for available WiFi networks.

        Returns:
            List of detected WiFi networks sorted by signal strength.
        """
        system = platform.system()

        if system == "Darwin":  # macOS
            return await WiFiScanner._scan_macos()
        elif system == "Linux":
            return await WiFiScanner._scan_linux()
        elif system == "Windows":
            return await WiFiScanner._scan_windows()
        else:
            logger.warning(f"WiFi scanning not supported on {system}")
            return []

    @staticmethod
    async def _scan_macos() -> list[WiFiNetwork]:
        """Scan WiFi networks on macOS."""
        try:
            result = subprocess.run(
                [
                    "/System/Library/PrivateFrameworks/Apple80211.framework"
                    "/Versions/Current/Resources/airport",
                    "-s",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            networks = []
            for line in result.stdout.strip().split("\n")[1:]:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 7:
                    ssid = parts[0]
                    bssid = parts[1]
                    rssi = int(parts[2])
                    channel = int(parts[3])
                    security = " ".join(parts[7:]) if len(parts) > 7 else "open"

                    networks.append(
                        WiFiNetwork(
                            ssid=ssid,
                            bssid=bssid,
                            signal_strength=rssi,
                            channel=channel,
                            security=security,
                        )
                    )

            return sorted(networks, key=lambda n: n.signal_strength, reverse=True)
        except Exception as e:
            logger.error(f"Failed to scan WiFi networks on macOS: {e}")
            return []

    @staticmethod
    async def _scan_linux() -> list[WiFiNetwork]:
        """Scan WiFi networks on Linux."""
        try:
            result = subprocess.run(
                ["nmcli", "dev", "wifi", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            networks = []
            for line in result.stdout.strip().split("\n")[1:]:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 6:
                    bssid = parts[0]
                    ssid = parts[1]
                    channel = int(parts[3])
                    signal = int(parts[4])
                    security = " ".join(parts[5:]) if len(parts) > 5 else "open"

                    networks.append(
                        WiFiNetwork(
                            ssid=ssid,
                            bssid=bssid,
                            signal_strength=signal,
                            channel=channel,
                            security=security,
                        )
                    )

            return sorted(networks, key=lambda n: n.signal_strength, reverse=True)
        except Exception as e:
            logger.error(f"Failed to scan WiFi networks on Linux: {e}")
            return []

    @staticmethod
    async def _scan_windows() -> list[WiFiNetwork]:
        """Scan WiFi networks on Windows."""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            networks = []
            current_network = None

            for line in result.stdout.split("\n"):
                if "SSID" in line and ":" in line:
                    ssid = line.split(":", 1)[1].strip()
                    current_network = {
                        "ssid": ssid,
                        "bssid": "",
                        "signal": 0,
                        "channel": 0,
                    }

                if current_network and "Signal" in line and ":" in line:
                    signal_str = line.split(":", 1)[1].strip().replace("%", "")
                    try:
                        signal_percent = int(signal_str)
                        current_network["signal"] = signal_percent
                        networks.append(
                            WiFiNetwork(
                                ssid=current_network["ssid"],
                                bssid=current_network.get("bssid", ""),
                                signal_strength=signal_percent,
                                channel=current_network.get("channel", 0),
                                security="WPA2",  # Default to WPA2 for Windows
                            )
                        )
                        current_network = None
                    except ValueError:
                        pass

            return sorted(networks, key=lambda n: n.signal_strength, reverse=True)
        except Exception as e:
            logger.error(f"Failed to scan WiFi networks on Windows: {e}")
            return []
