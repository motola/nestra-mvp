import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import type { BluetoothDeviceOut } from "@/lib/api/types";

interface BluetoothDeviceIn {
  mac_address: string;
  name: string;
  property_id: string;
  device_type?: string;
  rssi?: number;
  battery_level?: number | null;
}

interface BluetoothPairResponse {
  device_id: string;
  status: string;
  message: string;
}

interface BluetoothUnpairResponse {
  status: string;
  message: string;
}

export function useBluetoothDevices(propertyId?: string) {
  return useQuery({
    queryKey: ["bluetooth-devices", propertyId],
    queryFn: async () => {
      const url = propertyId
        ? `/integrations/bluetooth/devices?property_id=${propertyId}`
        : "/integrations/bluetooth/devices";
      return apiFetch<BluetoothDeviceOut[]>(url);
    },
  });
}

export function usePairBluetoothDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (device: BluetoothDeviceIn) => {
      return apiFetch<BluetoothPairResponse>("/integrations/bluetooth/pair", {
        method: "POST",
        body: JSON.stringify(device),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bluetooth-devices"] });
    },
  });
}

export function useUnpairBluetoothDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (deviceId: string) => {
      return apiFetch<BluetoothUnpairResponse>(
        `/integrations/bluetooth/unpair?device_id=${deviceId}`,
        {
          method: "POST",
        },
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bluetooth-devices"] });
    },
  });
}

/**
 * Scan for Bluetooth devices using Web Bluetooth API.
 * Returns array of devices or empty array if not supported or cancelled.
 */
export async function scanBluetoothDevices(): Promise<
  Array<{ name: string; mac_address: string }>
> {
  if (typeof navigator === "undefined" || !navigator.bluetooth) {
    throw new Error(
      "Web Bluetooth API not supported in this browser. Use Chrome 56+ or Edge 79+.",
    );
  }

  try {
    const device = await navigator.bluetooth.requestDevice({
      acceptAllDevices: true,
      optionalServices: [
        "0000180a-0000-1000-8000-00805f9b34fb", // Device Information
      ],
    });

    // In a real implementation, we'd scan multiple devices
    // For MVP, return the single selected device
    return [
      {
        name: device.name || "Unknown Device",
        mac_address: device.id, // BLE MAC or device ID
      },
    ];
  } catch (error) {
    if ((error as Error).name === "NotFoundError") {
      // User cancelled the dialog
      return [];
    }
    throw error;
  }
}
