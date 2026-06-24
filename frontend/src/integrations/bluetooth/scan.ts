/**Web Bluetooth API device scanning utility. */

import { ScannedDevice } from "./types";

// Extend Navigator to include bluetooth API
declare global {
  interface Navigator {
    bluetooth?: {
      requestDevice(options: {
        acceptAllDevices: boolean;
        optionalServices?: string[];
      }): Promise<{
        name?: string;
        id: string;
        gatt?: { connect(): Promise<void> };
      }>;
    };
  }
}

/**
 * Scan for Bluetooth devices using Web Bluetooth API.
 * Returns array of devices or empty array if not supported or cancelled.
 */
export async function scanBluetoothDevices(): Promise<ScannedDevice[]> {
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
