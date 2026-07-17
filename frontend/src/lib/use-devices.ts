"use client";

import { useState, useEffect } from "react";
import { DEVICES_MAPLE } from "@/lib/fixtures";
import type { Device } from "@/lib/fixtures";
import { useDemoMode } from "./use-demo-mode";

export function useDevices(propertyId?: string) {
  const { demoMode, isHydrated } = useDemoMode();
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isHydrated) return;

    async function fetchDevices() {
      try {
        setLoading(true);
        setError(null);

        if (demoMode) {
          // Use fixture data
          setDevices(DEVICES_MAPLE);
        } else {
          // Fetch from backend
          const url = propertyId
            ? `http://localhost:8000/properties/${propertyId}/devices`
            : "http://localhost:8000/devices";

          const res = await fetch(url);
          if (!res.ok)
            throw new Error(`Failed to fetch devices: ${res.status}`);
          const data = await res.json();
          setDevices(Array.isArray(data) ? data : data.devices || []);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
        // Fallback to empty array on error
        setDevices([]);
      } finally {
        setLoading(false);
      }
    }

    fetchDevices();
  }, [propertyId, demoMode, isHydrated]);

  return { devices, loading, error };
}
