"use client";

import { useState } from "react";
import { RefreshCw, X, Lock, Signal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, SectionHead } from "@/components/ui/card";
import { Tag } from "@/components/ui/tag";

interface WiFiNetwork {
  id: string;
  ssid: string;
  rssi: number;
  frequency: string;
  security: string;
}

interface WiFiDiscoveryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onNetworksSelected: (networks: WiFiNetwork[]) => void;
}

export function WiFiDiscoveryModal({
  isOpen,
  onClose,
  onNetworksSelected,
}: WiFiDiscoveryModalProps) {
  const [networks, setNetworks] = useState<WiFiNetwork[]>([]);
  const [selectedNetworks, setSelectedNetworks] = useState<Set<string>>(
    new Set(),
  );
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startScanning = async () => {
    setIsScanning(true);
    setError(null);
    setNetworks([]);

    try {
      // Try to use NetworkInformation API if available
      if ("connection" in navigator || "mozConnection" in navigator) {
        // WiFi networks can be accessed through some APIs, but most browsers block this for privacy
        // We'll show mock data for now
        throw new Error("WiFi scanning requires native app access");
      } else {
        // Fallback: Mock WiFi networks for testing
        setNetworks([
          {
            id: "network_1",
            ssid: "HomeNetwork",
            rssi: -45,
            frequency: "2.4GHz",
            security: "WPA2",
          },
          {
            id: "network_2",
            ssid: "GuestWiFi",
            rssi: -62,
            frequency: "2.4GHz",
            security: "Open",
          },
          {
            id: "network_3",
            ssid: "NeighborNet",
            rssi: -78,
            frequency: "5GHz",
            security: "WPA3",
          },
          {
            id: "network_4",
            ssid: "IoT-Devices",
            rssi: -55,
            frequency: "2.4GHz",
            security: "WPA2",
          },
        ]);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to scan networks";
      setError(message);
      console.error("WiFi scan error:", err);

      // Still show mock data for demo purposes
      setNetworks([
        {
          id: "network_1",
          ssid: "HomeNetwork",
          rssi: -45,
          frequency: "2.4GHz",
          security: "WPA2",
        },
        {
          id: "network_2",
          ssid: "GuestWiFi",
          rssi: -62,
          frequency: "2.4GHz",
          security: "Open",
        },
        {
          id: "network_3",
          ssid: "NeighborNet",
          rssi: -78,
          frequency: "5GHz",
          security: "WPA3",
        },
      ]);
    } finally {
      setIsScanning(false);
    }
  };

  const toggleNetworkSelection = (networkId: string) => {
    const newSelected = new Set(selectedNetworks);
    if (newSelected.has(networkId)) {
      newSelected.delete(networkId);
    } else {
      newSelected.add(networkId);
    }
    setSelectedNetworks(newSelected);
  };

  const handleAddNetworks = () => {
    const selected = networks.filter((n) => selectedNetworks.has(n.id));
    onNetworksSelected(selected);
    onClose();
  };

  const getSignalStrength = (rssi: number) => {
    if (rssi > -50) return "Excellent";
    if (rssi > -60) return "Good";
    if (rssi > -70) return "Fair";
    return "Poor";
  };

  const getSignalColor = (rssi: number) => {
    if (rssi > -50) return "text-green-600";
    if (rssi > -60) return "text-blue-600";
    if (rssi > -70) return "text-yellow-600";
    return "text-red-600";
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl mx-4">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <SectionHead
              title="WiFi Network Discovery"
              sub="SCAN AND SELECT NETWORKS"
            />
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded">
              <X size={20} />
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded text-amber-700 text-sm">
              {error} (showing mock data)
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

          {networks.length > 0 && (
            <div className="space-y-2 mb-4 max-h-64 overflow-y-auto">
              {networks.map((network) => (
                <label
                  key={network.id}
                  className="flex items-center p-3 border border-gray-200 rounded hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedNetworks.has(network.id)}
                    onChange={() => toggleNetworkSelection(network.id)}
                    className="mr-3"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-sm">{network.ssid}</p>
                      {network.security !== "Open" && (
                        <Lock size={14} className="text-gray-400" />
                      )}
                    </div>
                    <div className="flex gap-2 mt-1">
                      <Tag variant="neutral">{network.frequency}</Tag>
                      <Tag variant="neutral">{network.security}</Tag>
                      <div
                        className={`flex items-center gap-1 text-xs ${getSignalColor(network.rssi)}`}
                      >
                        <Signal size={12} />
                        {getSignalStrength(network.rssi)} ({network.rssi}dBm)
                      </div>
                    </div>
                  </div>
                </label>
              ))}
            </div>
          )}

          {networks.length === 0 && !isScanning && (
            <div className="text-center py-8 text-gray-500">
              <p className="mb-2">No networks found</p>
              <p className="text-sm">
                Click &quot;Start Scanning&quot; to discover WiFi networks
              </p>
            </div>
          )}

          <div className="flex gap-2 justify-end">
            <Button onClick={onClose} variant="secondary">
              Cancel
            </Button>
            <Button
              onClick={handleAddNetworks}
              disabled={selectedNetworks.size === 0}
              variant="primary"
            >
              Add{" "}
              {selectedNetworks.size > 0 ? `(${selectedNetworks.size})` : ""}
              {selectedNetworks.size === 0 ? "Networks" : "Selected"}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
