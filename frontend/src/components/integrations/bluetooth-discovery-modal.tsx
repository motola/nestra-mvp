"use client";

import { useState } from "react";
import { RefreshCw, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, SectionHead } from "@/components/ui/card";
import { Tag } from "@/components/ui/tag";

interface BluetoothDevice {
  id: string;
  name: string;
  rssi: number;
  services: string[];
}

interface BluetoothDiscoveryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDevicesSelected: (devices: BluetoothDevice[]) => void;
}

export function BluetoothDiscoveryModal({
  isOpen,
  onClose,
  onDevicesSelected,
}: BluetoothDiscoveryModalProps) {
  const [devices, setDevices] = useState<BluetoothDevice[]>([]);
  const [selectedDevices, setSelectedDevices] = useState<Set<string>>(
    new Set(),
  );
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startScanning = async () => {
    setIsScanning(true);
    setError(null);

    try {
      const bluetoothDevices: BluetoothDevice[] = [];

      // Try to use Web Bluetooth API if available
      if ("bluetooth" in navigator) {
        type BluetoothGATT = {
          connect: () => Promise<{
            getPrimaryServices: () => Promise<Array<{ uuid: string }>>;
          }>;
        };

        type BluetoothRequestDevice = {
          id: string;
          name: string;
          gatt: BluetoothGATT;
        };

        const device = await (
          navigator as unknown as {
            bluetooth: {
              requestDevice: (
                options: object,
              ) => Promise<BluetoothRequestDevice>;
            };
          }
        ).bluetooth.requestDevice({
          acceptAllDevices: true,
          optionalServices: [
            0x180a, // Device Information
            0x180f, // Battery Service
            0x181a, // Environmental Sensing
            0x1809, // Health Thermometer
            0x180d, // Heart Rate
            0x181e, // Body Composition
            0x1800, // Generic Access
            0x1801, // Generic Attribute
            0x180d, // Heart Rate Service
            0x181c, // User Data
          ],
        });

        let services: string[] = [];
        try {
          const gatt = await device.gatt.connect();
          const primaryServices = await gatt.getPrimaryServices();
          services = primaryServices.map((s: { uuid: string }) => s.uuid);
        } catch {
          // Services not available - device can still be added
          services = [];
        }

        bluetoothDevices.push({
          id: device.id,
          name: device.name || "Unknown Device",
          rssi: 0,
          services,
        });

        setDevices([...devices, ...bluetoothDevices]);
      } else {
        // Fallback: Mock BLE devices for testing
        setDevices([
          {
            id: "ble_sensor_temp_1",
            name: "BLE Temperature Sensor",
            rssi: -65,
            services: ["temperature", "battery"],
          },
          {
            id: "ble_sensor_contact_1",
            name: "BLE Door Contact Sensor",
            rssi: -72,
            services: ["contact", "battery"],
          },
          {
            id: "ble_sensor_motion_1",
            name: "BLE Motion Sensor",
            rssi: -58,
            services: ["motion", "battery"],
          },
        ]);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to pair device";
      setError(message);
      console.error("Bluetooth scan error:", err);
    } finally {
      setIsScanning(false);
    }
  };

  const toggleDeviceSelection = (deviceId: string) => {
    const newSelected = new Set(selectedDevices);
    if (newSelected.has(deviceId)) {
      newSelected.delete(deviceId);
    } else {
      newSelected.add(deviceId);
    }
    setSelectedDevices(newSelected);
  };

  const handleAddDevices = () => {
    const selected = devices.filter((d) => selectedDevices.has(d.id));
    onDevicesSelected(selected);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl mx-4">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <SectionHead
              title="Bluetooth Device Discovery"
              sub="SCAN AND SELECT BLE DEVICES"
            />
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded">
              <X size={20} />
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          <div className="mb-4">
            <Button
              onClick={startScanning}
              disabled={isScanning}
              variant="primary"
              className="w-full"
            >
              {isScanning && (
                <RefreshCw className="animate-spin mr-2" size={16} />
              )}
              {isScanning ? "Scanning..." : "Start Scanning"}
            </Button>
          </div>

          {devices.length > 0 && (
            <div className="space-y-2 mb-4 max-h-64 overflow-y-auto">
              {devices.map((device) => (
                <label
                  key={device.id}
                  className="flex items-center p-3 border border-gray-200 rounded hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedDevices.has(device.id)}
                    onChange={() => toggleDeviceSelection(device.id)}
                    className="mr-3"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-sm">{device.name}</p>
                    <p className="text-xs text-gray-500">
                      ID: {device.id} • RSSI: {device.rssi}dBm
                    </p>
                    {device.services.length > 0 && (
                      <div className="flex gap-1 mt-1 flex-wrap">
                        {device.services.slice(0, 3).map((service: string) => (
                          <Tag key={service} variant="neutral">
                            {service}
                          </Tag>
                        ))}
                        {device.services.length > 3 && (
                          <Tag variant="neutral">
                            +{device.services.length - 3}
                          </Tag>
                        )}
                      </div>
                    )}
                  </div>
                </label>
              ))}
            </div>
          )}

          {devices.length === 0 && !isScanning && (
            <div className="text-center py-8 text-gray-500">
              <p className="mb-2">No devices found</p>
              <p className="text-sm">
                Click &quot;Start Scanning&quot; to discover Bluetooth devices
              </p>
            </div>
          )}

          <div className="flex gap-2 justify-end">
            <Button onClick={onClose} variant="secondary">
              Cancel
            </Button>
            <Button
              onClick={handleAddDevices}
              disabled={selectedDevices.size === 0}
              variant="primary"
            >
              {selectedDevices.size === 0
                ? "Add Devices"
                : `Add Selected (${selectedDevices.size})`}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
