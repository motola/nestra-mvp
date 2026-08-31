"use client";

import { useState, useEffect } from "react";
import { X, Loader } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tag } from "@/components/ui/tag";
import { VendorLogo } from "@/components/integrations/vendor-logos";
import type { Vendor } from "@/lib/fixtures";

interface BluetoothDevice {
  id: string;
  name: string;
  rssi: number;
  services: string[];
}

interface WiFiNetwork {
  ssid: string;
  bssid: string;
  signal_strength: number;
  channel: number;
  security: string;
}

interface ScanState {
  bluetooth: { scanning: boolean; devices: BluetoothDevice[] };
  wifi: { scanning: boolean; networks: WiFiNetwork[] };
  error: string | null;
}

export function ConnectVendorModal({
  isOpen,
  vendor,
  onClose,
  onDevicesSelected,
}: {
  isOpen: boolean;
  vendor: Vendor;
  onClose: () => void;
  onDevicesSelected: (
    bluetoothDevices: BluetoothDevice[],
    wifiNetworks: WiFiNetwork[],
  ) => void;
}) {
  const [scanState, setScanState] = useState<ScanState>({
    bluetooth: { scanning: true, devices: [] },
    wifi: { scanning: true, networks: [] },
    error: null,
  });
  const [selectedDevices, setSelectedDevices] = useState<Set<string>>(
    new Set(),
  );
  const [selectedNetworks, setSelectedNetworks] = useState<Set<string>>(
    new Set(),
  );

  useEffect(() => {
    if (!isOpen) return;

    const scanDevices = async () => {
      try {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        setScanState((prev) => ({
          ...prev,
          bluetooth: { scanning: false, devices: [] },
        }));
      } catch {
        setScanState((prev) => ({
          ...prev,
          bluetooth: { scanning: false, devices: [] },
          error: "Bluetooth scan failed",
        }));
      }
    };

    const scanNetworks = async () => {
      try {
        await new Promise((resolve) => setTimeout(resolve, 1500));
        setScanState((prev) => ({
          ...prev,
          wifi: { scanning: false, networks: [] },
        }));
      } catch {
        setScanState((prev) => ({
          ...prev,
          wifi: { scanning: false, networks: [] },
          error: "WiFi scan failed",
        }));
      }
    };

    scanDevices();
    scanNetworks();
  }, [isOpen]);

  const isScanning = scanState.bluetooth.scanning || scanState.wifi.scanning;

  const handleConfirm = () => {
    const selectedBT = scanState.bluetooth.devices.filter((d) =>
      selectedDevices.has(d.id),
    );
    const selectedWiFi = scanState.wifi.networks.filter((n) =>
      selectedNetworks.has(n.bssid),
    );

    onDevicesSelected(selectedBT, selectedWiFi);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-bg rounded-lg shadow-lg w-full max-w-2xl max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <VendorLogo name={vendor.name} size={32} />
            <div>
              <h2 className="text-[16px] font-semibold text-text m-0">
                Connect {vendor.name}
              </h2>
              <p className="text-[13px] text-text-3 mt-0.5 m-0">
                Scanning local area network...
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-surface rounded-lg border-0 cursor-pointer bg-transparent"
          >
            <X size={20} className="text-text-2" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {scanState.error && (
            <div className="bg-red-100 text-red-700 p-4 rounded-lg text-sm">
              {scanState.error}
            </div>
          )}

          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <h3 className="text-[14px] font-semibold text-text m-0">
                Bluetooth Devices
              </h3>
              {scanState.bluetooth.scanning && (
                <Loader size={16} className="text-accent animate-spin" />
              )}
            </div>

            {scanState.bluetooth.scanning ? (
              <div className="text-[13px] text-text-3 text-center py-8">
                Scanning for Bluetooth devices...
              </div>
            ) : scanState.bluetooth.devices.length > 0 ? (
              <div className="space-y-2">
                {scanState.bluetooth.devices.map((device) => (
                  <label
                    key={device.id}
                    className="flex items-center gap-3 p-3 border border-border rounded-lg cursor-pointer hover:bg-surface"
                  >
                    <input
                      type="checkbox"
                      checked={selectedDevices.has(device.id)}
                      onChange={(e) => {
                        const newSet = new Set(selectedDevices);
                        if (e.target.checked) {
                          newSet.add(device.id);
                        } else {
                          newSet.delete(device.id);
                        }
                        setSelectedDevices(newSet);
                      }}
                      className="cursor-pointer"
                    />
                    <div className="flex-1">
                      <p className="text-[13px] font-medium text-text m-0">
                        {device.name}
                      </p>
                      <p className="text-[11px] text-text-3 mt-0.5 m-0">
                        {device.id} · {device.rssi} dBm
                      </p>
                    </div>
                    <Tag variant="neutral">
                      {device.services.length} services
                    </Tag>
                  </label>
                ))}
              </div>
            ) : (
              <div className="text-[13px] text-text-3 py-4 text-center">
                No Bluetooth devices found
              </div>
            )}
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <h3 className="text-[14px] font-semibold text-text m-0">
                WiFi Networks
              </h3>
              {scanState.wifi.scanning && (
                <Loader size={16} className="text-accent animate-spin" />
              )}
            </div>

            {scanState.wifi.scanning ? (
              <div className="text-[13px] text-text-3 text-center py-8">
                Scanning for WiFi networks...
              </div>
            ) : scanState.wifi.networks.length > 0 ? (
              <div className="space-y-2">
                {scanState.wifi.networks.map((network) => (
                  <label
                    key={network.bssid}
                    className="flex items-center gap-3 p-3 border border-border rounded-lg cursor-pointer hover:bg-surface"
                  >
                    <input
                      type="checkbox"
                      checked={selectedNetworks.has(network.bssid)}
                      onChange={(e) => {
                        const newSet = new Set(selectedNetworks);
                        if (e.target.checked) {
                          newSet.add(network.bssid);
                        } else {
                          newSet.delete(network.bssid);
                        }
                        setSelectedNetworks(newSet);
                      }}
                      className="cursor-pointer"
                    />
                    <div className="flex-1">
                      <p className="text-[13px] font-medium text-text m-0">
                        {network.ssid}
                      </p>
                      <p className="text-[11px] text-text-3 mt-0.5 m-0">
                        {network.bssid} · Ch {network.channel} ·{" "}
                        {network.security}
                      </p>
                    </div>
                    <Tag variant="neutral">{network.signal_strength} dBm</Tag>
                  </label>
                ))}
              </div>
            ) : (
              <div className="text-[13px] text-text-3 py-4 text-center">
                No WiFi networks found
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-2 p-6 border-t border-border">
          <Button variant="secondary" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleConfirm}
            disabled={
              isScanning ||
              (selectedDevices.size === 0 && selectedNetworks.size === 0)
            }
          >
            {isScanning ? "Scanning..." : "Connect Selected Devices"}
          </Button>
        </div>
      </div>
    </div>
  );
}
