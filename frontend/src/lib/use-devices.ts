"use client";

import { useState, useEffect } from "react";
import { getToken } from "@/lib/auth/session";
import type { Device, DeviceCategory } from "@/lib/fixtures";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface BackendDevice {
  id: string;
  name: string;
  vendor: string;
  vendor_name: string;
  device_type: string;
  online: boolean;
  created_at: string;
}

function convertBackendDevice(bd: BackendDevice): Device {
  // Map backend device_type to frontend category
  const categoryMap: Record<string, DeviceCategory> = {
    SENSOR: "SENSOR_MOTION",
    PLUG: "PLUG",
    LIGHT: "LIGHT",
    LOCK: "LOCK",
    THERMOSTAT: "THERMOSTAT",
    SWITCH: "SWITCH",
    HUB: "HUB",
  };

  return {
    id: bd.id,
    name: bd.vendor_name || bd.name,
    room: "Unknown",
    category: categoryMap[bd.device_type] || "PLUG",
    vendor: bd.vendor,
    owner: "property",
    state: bd.online ? "On" : "Off",
    reachable: bd.online,
    alert: false,
    lastSeen: new Date(bd.created_at).toLocaleString(),
    capabilities: [],
  };
}

export function useDevices(propertyId?: string) {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!propertyId) {
      setDevices([]);
      setLoading(false);
      setError(null);
      return;
    }

    async function fetchDevices() {
      try {
        setLoading(true);
        setError(null);

        const token = getToken();
        if (!token) {
          throw new Error("Not authenticated");
        }

        const url = `${API_BASE}/properties/${propertyId}/devices`;

        const res = await fetch(url, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!res.ok) {
          throw new Error(`Failed to fetch devices: ${res.status}`);
        }
        const backendDevices: BackendDevice[] = await res.json();
        setDevices(backendDevices.map(convertBackendDevice));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
        setDevices([]);
      } finally {
        setLoading(false);
      }
    }

    fetchDevices();
  }, [propertyId]);

  return { devices, loading, error };
}
