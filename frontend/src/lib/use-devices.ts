"use client";

import { useState, useEffect } from "react";
import type { Device } from "@/lib/fixtures";

interface BackendDevice {
  id: string;
  name: string;
  vendor: string;
  online: boolean;
}

function convertBackendDevice(bd: BackendDevice): Device {
  return {
    id: bd.id,
    name: bd.name,
    room: "Unknown",
    category: "PLUG",
    vendor: bd.vendor,
    owner: "property",
    state: bd.online ? "On" : "Off",
    reachable: bd.online,
    alert: false,
    lastSeen: "now",
    capabilities: [],
  };
}

export function useDevices(propertyId?: string) {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDevices() {
      try {
        setLoading(true);
        setError(null);

        if (!propertyId) {
          throw new Error("propertyId is required to fetch devices");
        }
        const url = `http://localhost:8000/properties/${propertyId}/devices`;

        const res = await fetch(url);
        if (!res.ok) throw new Error(`Failed to fetch devices: ${res.status}`);
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
