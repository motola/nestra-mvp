"use client";

import { useState } from "react";
import { Search, Loader, CheckCircle, AlertCircle, Wifi } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  scanBluetoothDevices,
  usePairBluetoothDevice,
} from "@/lib/api/hooks/use-bluetooth";

interface BluetoothPairingModalProps {
  propertyId: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

interface ScannedDevice {
  name: string;
  mac_address: string;
}

type ModalState =
  | "initial"
  | "scanning"
  | "selecting"
  | "pairing"
  | "success"
  | "error";

export function BluetoothPairingModal({
  propertyId,
  onSuccess,
  onCancel,
}: BluetoothPairingModalProps) {
  const [state, setState] = useState<ModalState>("initial");
  const [devices, setDevices] = useState<ScannedDevice[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<ScannedDevice | null>(
    null,
  );
  const [error, setError] = useState<string>("");

  const pairMutation = usePairBluetoothDevice();

  const handleScan = async () => {
    setState("scanning");
    setError("");
    try {
      const found = await scanBluetoothDevices();
      if (found.length === 0) {
        setError(
          "No Bluetooth devices found. Make sure your device is powered on and in range.",
        );
        setState("error");
      } else {
        setDevices(found);
        setState("selecting");
      }
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to scan for devices";
      setError(errorMsg);
      setState("error");
    }
  };

  const handlePairDevice = async (device: ScannedDevice) => {
    setSelectedDevice(device);
    setState("pairing");

    try {
      await pairMutation.mutateAsync({
        mac_address: device.mac_address,
        name: device.name,
        property_id: propertyId,
        device_type: "unknown",
        rssi: -60,
      });

      setState("success");
      setTimeout(() => {
        onSuccess?.();
      }, 1500);
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to pair device";
      setError(errorMsg);
      setState("error");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <Card className="w-96 p-6 shadow-lg">
        {state === "initial" && (
          <>
            <h2 className="text-[18px] font-semibold text-text mb-2">
              Pair Bluetooth Device
            </h2>
            <p className="text-[13px] text-text-2 mb-6">
              Scan for nearby Bluetooth devices and pair them to this property.
            </p>
            <div className="flex gap-3">
              <Button
                variant="primary"
                onClick={handleScan}
                className="flex-1 flex items-center justify-center gap-2"
              >
                <Search size={14} />
                Scan Devices
              </Button>
              <Button variant="ghost" onClick={onCancel}>
                Cancel
              </Button>
            </div>
          </>
        )}

        {state === "scanning" && (
          <>
            <div className="flex items-center justify-center py-8">
              <Loader className="animate-spin" size={32} />
            </div>
            <p className="text-center text-[13px] text-text-2">
              Scanning for Bluetooth devices...
            </p>
          </>
        )}

        {state === "selecting" && (
          <>
            <h2 className="text-[18px] font-semibold text-text mb-4">
              Found {devices.length} Device{devices.length !== 1 ? "s" : ""}
            </h2>
            <div className="space-y-2 mb-4 max-h-64 overflow-y-auto">
              {devices.map((device, idx) => (
                <button
                  key={idx}
                  onClick={() => handlePairDevice(device)}
                  className="w-full text-left p-3 bg-surface border border-border rounded-[9px] hover:border-accent hover:bg-surface-2 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Wifi size={14} className="text-accent" />
                    <div className="flex-1 min-w-0">
                      <p className="text-[13px] font-medium text-text truncate">
                        {device.name}
                      </p>
                      <p className="text-[11px] text-text-3 font-mono">
                        {device.mac_address}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
            <div className="flex gap-3">
              <Button variant="ghost" onClick={handleScan} className="flex-1">
                Scan Again
              </Button>
              <Button variant="ghost" onClick={onCancel}>
                Cancel
              </Button>
            </div>
          </>
        )}

        {state === "pairing" && (
          <>
            <div className="flex items-center justify-center py-8">
              <Loader className="animate-spin" size={32} />
            </div>
            <p className="text-center text-[13px] text-text-2 mb-2">
              Pairing {selectedDevice?.name}...
            </p>
            <p className="text-center text-[11px] text-text-3">
              {selectedDevice?.mac_address}
            </p>
          </>
        )}

        {state === "success" && (
          <>
            <div className="flex items-center justify-center py-8">
              <CheckCircle className="text-accent" size={48} />
            </div>
            <p className="text-center text-[13px] font-medium text-text mb-1">
              Device Paired Successfully
            </p>
            <p className="text-center text-[12px] text-text-2">
              {selectedDevice?.name} is now connected
            </p>
          </>
        )}

        {state === "error" && (
          <>
            <div className="flex items-center gap-3 mb-4 p-3 bg-red-bg border border-red rounded-[9px]">
              <AlertCircle size={18} className="text-red shrink-0" />
              <div>
                <p className="text-[12px] font-medium text-red mb-1">Error</p>
                <p className="text-[11px] text-red-dark">{error}</p>
              </div>
            </div>
            <div className="flex gap-3">
              <Button variant="primary" onClick={handleScan} className="flex-1">
                Try Again
              </Button>
              <Button variant="ghost" onClick={onCancel}>
                Cancel
              </Button>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
