"""WiFi scanning API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from integrations.wifi.scanner import WiFiScanner

router = APIRouter(prefix="/wifi", tags=["wifi"])


class WiFiNetworkResponse(BaseModel):
    """WiFi network response."""

    ssid: str
    bssid: str
    signal_strength: int
    channel: int
    security: str


@router.post("/scan", response_model=list[WiFiNetworkResponse])
async def scan_wifi_networks() -> list[WiFiNetworkResponse]:
    """Scan for available WiFi networks.

    Returns a list of detected WiFi networks sorted by signal strength.
    Requires system-level permissions to scan networks.
    """
    try:
        networks = await WiFiScanner.scan()
        return [
            WiFiNetworkResponse(
                ssid=n.ssid,
                bssid=n.bssid,
                signal_strength=n.signal_strength,
                channel=n.channel,
                security=n.security,
            )
            for n in networks
        ]
    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail="WiFi scanning requires elevated permissions (admin/root)",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WiFi scanning failed: {str(e)}") from e
