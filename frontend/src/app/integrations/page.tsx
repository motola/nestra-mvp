"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Wifi,
  Search,
  Smartphone,
  CheckCircle,
  XCircle,
  Loader2,
  ChevronRight,
  ArrowLeft,
  Plus,
  Cloud,
  Sun,
  Cpu,
} from "lucide-react";
import { provisioningApi, roomsApi, streamProvision, streamCommissionMatter, integrationsApi, propertiesApi } from "@/lib/api";
import type { Property, Room, ScannedDevice, CommissionedDeviceInfo, VendorIntegration } from "@/lib/types";

type View = "main" | "hotspot-list" | "provision-config" | "provision-progress" | "scan-network" | "matter";
type MatterSubView = "choose" | "commission" | "commissioning" | "commission-success" | "scan";

// ── Vendor badge colours ───────────────────────────────────────────────────────



// ── Room selector with inline "Add new room" ──────────────────────────────────

function RoomSelector({
  propertyId,
  value,
  onChange,
}: {
  propertyId: string;
  value: string;
  onChange: (v: string) => void;
}) {
  const [adding, setAdding] = useState(false);
  const [newName, setNewName] = useState("");
  const queryClient = useQueryClient();

  const { data: rooms = [] } = useQuery<Room[]>({
    queryKey: ["rooms", propertyId],
    queryFn: () => roomsApi.list(propertyId),
    enabled: !!propertyId,
  });

  const createMut = useMutation({
    mutationFn: (name: string) => roomsApi.create(propertyId, { name }),
    onSuccess: (room) => {
      queryClient.invalidateQueries({ queryKey: ["rooms", propertyId] });
      onChange(room.id);
      setAdding(false);
      setNewName("");
    },
  });

  if (!propertyId) return null;

  return (
    <div className="space-y-2">
      <label className="block text-xs text-text-2">Room (optional)</label>
      {adding ? (
        <div className="flex gap-2">
          <input
            autoFocus
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Room name"
            className="flex-1 bg-surface-2 border border-border rounded-lg px-3 py-2 text-sm text-text placeholder-gray-500 focus:outline-none focus:border-blue-500"
            onKeyDown={(e) => {
              if (e.key === "Enter" && newName.trim()) createMut.mutate(newName.trim());
              if (e.key === "Escape") setAdding(false);
            }}
          />
          <button
            onClick={() => newName.trim() && createMut.mutate(newName.trim())}
            disabled={createMut.isPending}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm text-text disabled:opacity-50"
          >
            {createMut.isPending ? <Loader2 size={14} className="animate-spin" /> : "Add"}
          </button>
          <button
            onClick={() => setAdding(false)}
            className="px-3 py-2 bg-surface-2 hover:bg-gray-600 rounded-lg text-sm text-text-2"
          >
            Cancel
          </button>
        </div>
      ) : (
        <div className="flex gap-2">
          <select
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="flex-1 bg-surface-2 border border-border rounded-lg px-3 py-2 text-sm text-text focus:outline-none focus:border-blue-500"
          >
            <option value="">No room assigned</option>
            {rooms.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
          <button
            onClick={() => setAdding(true)}
            className="px-3 py-2 bg-surface-2 hover:bg-gray-600 rounded-lg text-sm text-text-2 flex items-center gap-1"
          >
            <Plus size={12} /> New room
          </button>
        </div>
      )}
    </div>
  );
}

// ── Save device modal ─────────────────────────────────────────────────────────

function SaveDeviceModal({
  device,
  properties,
  onSave,
  onClose,
}: {
  device: ScannedDevice;
  properties: Property[];
  onSave: (propertyId: string, roomId: string, name: string) => void;
  onClose: () => void;
}) {
  const [name, setName] = useState(device.name || device.model || "");
  const [propertyId, setPropertyId] = useState("");
  const [roomId, setRoomId] = useState("");

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-surface border border-border rounded-2xl p-6 w-full max-w-md space-y-4">
        <h3 className="text-base font-semibold text-text">Add Device</h3>
        <div className="space-y-3">
          <div>
            <label className="block text-xs text-text-2 mb-1">Device Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter a name for this device"
              className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2 text-sm text-text placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs text-text-2 mb-1">Property</label>
            <select
              value={propertyId}
              onChange={(e) => { setPropertyId(e.target.value); setRoomId(""); }}
              className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2 text-sm text-text focus:outline-none focus:border-blue-500"
            >
              <option value="">No property</option>
              {properties.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          {propertyId && (
            <RoomSelector propertyId={propertyId} value={roomId} onChange={setRoomId} />
          )}
        </div>
        <div className="flex gap-2 pt-2">
          <button
            onClick={() => onSave(propertyId, roomId, name.trim() || device.name)}
            disabled={!name.trim()}
            className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 rounded-lg text-sm text-text font-medium"
          >
            Add Device
          </button>
          <button
            onClick={onClose}
            className="flex-1 py-2 bg-surface-2 hover:bg-gray-600 rounded-lg text-sm text-text-2"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function IntegrationsPage() {
  const queryClient = useQueryClient();
  const [view, setView] = useState<View>("main");
  const [matterSubView, setMatterSubView] = useState<MatterSubView>("choose");

  // Provision flow state
  const [selectedHotspot, setSelectedHotspot] = useState("");
  const [wifiSsid, setWifiSsid] = useState("");
  const [wifiPassword, setWifiPassword] = useState("");
  const [provisionPropertyId, setProvisionPropertyId] = useState("");
  const [provisionRoomId, setProvisionRoomId] = useState("");
  const [provisionLog, setProvisionLog] = useState<string[]>([]);
  const [provisionDone, setProvisionDone] = useState(false);
  const [provisionError, setProvisionError] = useState("");
  const [provisionedDevice, setProvisionedDevice] = useState<ScannedDevice | null>(null);

  // Scan flow state
  const [saveTarget, setSaveTarget] = useState<ScannedDevice | null>(null);

  // Matter commission state
  const [matterSetupCode, setMatterSetupCode] = useState("");
  const [matterPropertyId, setMatterPropertyId] = useState("");
  const [matterRoomId, setMatterRoomId] = useState("");
  const [commissionedDevice, setCommissionedDevice] = useState<CommissionedDeviceInfo | null>(null);
  const [commissionError, setCommissionError] = useState("");
  const [commissionLog, setCommissionLog] = useState<string[]>([]);

  // Matter scan state
  const [matterDevices, setMatterDevices] = useState<ScannedDevice[]>([]);
  const [matterScanning, setMatterScanning] = useState(false);

  // Queries
  const { data: properties = [] } = useQuery({
    queryKey: ["properties"],
    queryFn: propertiesApi.list,
  });

  const { data: savedDevices = [], isLoading: devicesLoading } = useQuery({
    queryKey: ["saved-devices"],
    queryFn: () => provisioningApi.listDevices(),
  });

  const { data: integrations = [] } = useQuery<VendorIntegration[]>({
    queryKey: ["integrations"],
    queryFn: integrationsApi.list,
  });

  const { data: hotspots = [], isLoading: hotspotLoading } = useQuery({
    queryKey: ["hotspots"],
    queryFn: provisioningApi.hotspots,
    enabled: view === "hotspot-list",
  });

  const { data: networkScan = [], isLoading: scanLoading, refetch: refetchScan } = useQuery({
    queryKey: ["network-scan"],
    queryFn: provisioningApi.scan,
    enabled: view === "scan-network",
    staleTime: 0,
  });

  // Mutations
  const saveMut = useMutation({
    mutationFn: (data: Parameters<typeof provisioningApi.saveDevice>[0]) =>
      provisioningApi.saveDevice(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saved-devices"] });
      setSaveTarget(null);
    },
  });

  async function startMatterCommission() {
    setCommissionLog([]);
    setCommissionedDevice(null);
    setCommissionError("");
    setMatterSubView("commissioning");
    try {
      await streamCommissionMatter(
        { setup_code: matterSetupCode, property_id: matterPropertyId, room_id: matterRoomId },
        (event) => {
          if (event.type === "status" && event.message) {
            setCommissionLog((l) => [...l, event.message!]);
          }
          if (event.type === "device" && event.device) {
            setCommissionedDevice(event.device);
          }
          if (event.type === "error" && event.message) {
            setCommissionError(event.message);
          }
          if (event.type === "done") {
            queryClient.invalidateQueries({ queryKey: ["saved-devices"] });
            setMatterSubView("commission-success");
          }
        },
      );
    } catch (err) {
      setCommissionError(String(err));
      setMatterSubView("commission-success");
    }
  }

  // ── Provision flow ───────────────────────────────────────────────────────────

  async function startProvision() {
    setProvisionLog([]);
    setProvisionDone(false);
    setProvisionError("");
    setProvisionedDevice(null);
    setView("provision-progress");

    try {
      await streamProvision(
        {
          hotspot_name: selectedHotspot,
          wifi_ssid: wifiSsid,
          wifi_password: wifiPassword,
          property_id: provisionPropertyId,
          room_id: provisionRoomId || undefined,
        },
        (event) => {
          if (event.type === "status" && event.message) {
            setProvisionLog((l) => [...l, event.message!]);
          }
          if (event.type === "device" && event.device) {
            setProvisionedDevice(event.device);
          }
          if (event.type === "error" && event.message) {
            setProvisionError(event.message);
          }
          if (event.type === "done") {
            setProvisionDone(true);
          }
        },
      );
    } catch (err) {
      setProvisionError(String(err));
      setProvisionDone(true);
    }
  }

  async function saveProvisionedDevice() {
    if (!provisionedDevice) return;
    await saveMut.mutateAsync({
      vendor: provisionedDevice.vendor,
      name: provisionedDevice.name,
      model: provisionedDevice.model,
      ip: provisionedDevice.ip,
      mac: provisionedDevice.mac,
      property_id: provisionPropertyId,
      room_id: provisionRoomId || undefined,
    });
    resetAndGoHome();
  }

  function resetAndGoHome() {
    setView("main");
    setSelectedHotspot("");
    setWifiSsid("");
    setWifiPassword("");
    setProvisionPropertyId("");
    setProvisionRoomId("");
    setProvisionLog([]);
    setProvisionDone(false);
    setProvisionError("");
    setProvisionedDevice(null);
  }

  // ── Matter scan ──────────────────────────────────────────────────────────────

  async function runMatterScan() {
    setMatterScanning(true);
    setMatterDevices([]);
    try {
      const devices = await provisioningApi.scanMatter();
        setMatterDevices(devices);
    } finally {
      setMatterScanning(false);
    }
  }

  // ── Shared back button ───────────────────────────────────────────────────────

  function BackButton({ label = "Back", onClick }: { label?: string; onClick: () => void }) {
    return (
      <button
        onClick={onClick}
        className="flex items-center gap-1.5 text-sm text-text-2 hover:text-text mb-5 transition-colors"
      >
        <ArrowLeft size={14} /> {label}
      </button>
    );
  }

  // ── Views ────────────────────────────────────────────────────────────────────

  if (view === "hotspot-list") {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <BackButton onClick={() => setView("main")} />
        <h2 className="text-lg font-bold text-text mb-1">Set Up New Device</h2>
        <p className="text-sm text-text-2 mb-5">Select your Shelly device from the list below.</p>
        {hotspotLoading ? (
          <div className="flex items-center gap-2 text-text-2 text-sm">
            <Loader2 size={16} className="animate-spin" /> Scanning for device hotspots...
          </div>
        ) : hotspots.length === 0 ? (
          <div className="bg-surface border border-border rounded-xl p-6 text-center">
            <p className="text-text-2 text-sm">No device hotspots found.</p>
            <p className="text-text-3 text-xs mt-1">Make sure your Shelly device is in setup mode (LED flashing).</p>
          </div>
        ) : (
          <div className="space-y-2">
            {hotspots.map((h) => (
              <button
                key={h}
                onClick={() => { setSelectedHotspot(h); setView("provision-config"); }}
                className="w-full flex items-center justify-between bg-surface border border-border hover:border-border-strong rounded-xl p-4 text-left transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Wifi size={16} className="text-amber" />
                  <span className="text-sm text-text">{h}</span>
                </div>
                <ChevronRight size={14} className="text-text-3" />
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (view === "provision-config") {
    return (
      <div className="p-6 max-w-md mx-auto">
        <BackButton onClick={() => setView("hotspot-list")} />
        <h2 className="text-lg font-bold text-text mb-1">Configure Device</h2>
        <p className="text-sm text-text-2 mb-5">
          Setting up: <span className="text-text font-medium">{selectedHotspot}</span>
        </p>
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-text-2 mb-1">Your WiFi Network Name</label>
            <input
              value={wifiSsid}
              onChange={(e) => setWifiSsid(e.target.value)}
              placeholder="e.g. MyHomeNetwork"
              className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2.5 text-sm text-text placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs text-text-2 mb-1">WiFi Password</label>
            <input
              type="password"
              value={wifiPassword}
              onChange={(e) => setWifiPassword(e.target.value)}
              placeholder="Your WiFi password"
              className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2.5 text-sm text-text placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
            <p className="text-xs text-text-3 mt-1">Used once to set up the device, never stored.</p>
          </div>
          <div>
            <label className="block text-xs text-text-2 mb-1">Property (optional)</label>
            <select
              value={provisionPropertyId}
              onChange={(e) => { setProvisionPropertyId(e.target.value); setProvisionRoomId(""); }}
              className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2.5 text-sm text-text focus:outline-none focus:border-blue-500"
            >
              <option value="">No property</option>
              {properties.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          {provisionPropertyId && (
            <RoomSelector
              propertyId={provisionPropertyId}
              value={provisionRoomId}
              onChange={setProvisionRoomId}
            />
          )}
          <button
            onClick={startProvision}
            disabled={!wifiSsid}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 rounded-lg text-sm text-text font-medium mt-2 transition-colors"
          >
            Set Up Device
          </button>
        </div>
      </div>
    );
  }

  if (view === "provision-progress") {
    return (
      <div className="p-6 max-w-md mx-auto">
        <h2 className="text-lg font-bold text-text mb-5">Setting Up Device</h2>
        <div className="bg-surface border border-border rounded-xl p-4 space-y-2 mb-4 min-h-[120px]">
          {provisionLog.map((msg, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-text-2">
              <CheckCircle size={13} className="text-green shrink-0" />
              {msg}
            </div>
          ))}
          {!provisionDone && (
            <div className="flex items-center gap-2 text-sm text-text-3">
              <Loader2 size={13} className="animate-spin shrink-0" />
              Working...
            </div>
          )}
        </div>

        {provisionDone && provisionError && (
          <div className="bg-red-900/30 border border-red-700/40 rounded-xl p-4 mb-4">
            <div className="flex items-center gap-2 text-sm text-red">
              <XCircle size={14} />
              {provisionError}
            </div>
          </div>
        )}

        {provisionDone && provisionedDevice && !provisionError && (
          <div className="bg-green-900/20 border border-green-700/30 rounded-xl p-4 mb-4">
            <p className="text-sm text-green font-medium mb-1">{provisionedDevice.name}</p>
            <p className="text-xs text-text-2">{provisionedDevice.model}</p>
          </div>
        )}

        {provisionDone && (
          <div className="flex gap-2">
            {provisionedDevice && !provisionError && (
              <button
                onClick={saveProvisionedDevice}
                disabled={saveMut.isPending}
                className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm text-text font-medium disabled:opacity-50"
              >
                {saveMut.isPending ? "Saving..." : "Save Device"}
              </button>
            )}
            <button
              onClick={resetAndGoHome}
              className="flex-1 py-2.5 bg-surface-2 hover:bg-gray-600 rounded-lg text-sm text-text-2"
            >
              Done
            </button>
          </div>
        )}
      </div>
    );
  }

  if (view === "scan-network") {
    const grouped = networkScan.reduce<Record<string, ScannedDevice[]>>((acc, d) => {
      (acc[d.vendor] ??= []).push(d);
      return acc;
    }, {});

    return (
      <div className="p-6 max-w-3xl mx-auto">
        <BackButton onClick={() => setView("main")} />
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-lg font-bold text-text">Find Devices on Network</h2>
            <p className="text-sm text-text-2">Devices already connected to your WiFi</p>
          </div>
          <button
            onClick={() => refetchScan()}
            className="flex items-center gap-1.5 text-sm text-text-2 hover:text-text-2"
          >
            <Search size={14} /> Scan again
          </button>
        </div>

        {scanLoading ? (
          <div className="flex items-center gap-2 text-text-2 text-sm">
            <Loader2 size={16} className="animate-spin" /> Scanning network...
          </div>
        ) : networkScan.length === 0 ? (
          <div className="bg-surface border border-border rounded-xl p-6 text-center">
            <p className="text-text-2 text-sm">No devices found on network.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(grouped).map(([vendor, devices]) => (
              <div key={vendor}>
                <h3 className="text-xs font-semibold text-text-3 uppercase tracking-widest mb-2">
                  {vendor}
                </h3>
                <div className="space-y-2">
                  {devices.map((d, i) => {
                    const alreadySaved = savedDevices.some((s) => s.mac === d.mac && d.mac);
                    return (
                      <div
                        key={i}
                        className="flex items-center justify-between bg-surface border border-border rounded-xl px-4 py-3"
                      >
                        <div>
                          <p className="text-sm text-text font-medium">{d.name}</p>
                          <p className="text-xs text-text-3">{d.model}</p>
                        </div>
                        {alreadySaved ? (
                          <span className="text-xs text-green flex items-center gap-1">
                            <CheckCircle size={12} /> Added
                          </span>
                        ) : (
                          <button
                            onClick={() => setSaveTarget(d)}
                            className="text-sm text-text-2 hover:text-text-2 flex items-center gap-1"
                          >
                            <Plus size={13} /> Add
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {saveTarget && (
          <SaveDeviceModal
            device={saveTarget}
            properties={properties}
            onSave={(propId, roomId, name) => {
              saveMut.mutate({
                vendor: saveTarget.vendor,
                name,
                model: saveTarget.model,
                ip: saveTarget.ip,
                mac: saveTarget.mac,
                property_id: propId,
                room_id: roomId || null,
              });
            }}
            onClose={() => setSaveTarget(null)}
          />
        )}
      </div>
    );
  }

  if (view === "matter") {
    if (matterSubView === "commission") {
      return (
        <div className="p-6 max-w-md mx-auto">
          <BackButton onClick={() => setMatterSubView("choose")} />
          <h2 className="text-lg font-bold text-text mb-1">Commission Matter Device</h2>
          <p className="text-sm text-text-2 mb-5">Enter the setup code from your device packaging.</p>
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-text-2 mb-1">Setup Code</label>
              <input
                value={matterSetupCode}
                onChange={(e) => setMatterSetupCode(e.target.value)}
                placeholder="e.g. 1234-567-8901"
                className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2.5 text-sm text-text placeholder-gray-500 focus:outline-none focus:border-green-500 font-mono tracking-wide"
              />
            </div>
            <div>
              <label className="block text-xs text-text-2 mb-1">Property (optional)</label>
              <select
                value={matterPropertyId}
                onChange={(e) => { setMatterPropertyId(e.target.value); setMatterRoomId(""); }}
                className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2.5 text-sm text-text focus:outline-none focus:border-green-500"
              >
                <option value="">No property</option>
                {properties.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
            {matterPropertyId && (
              <RoomSelector
                propertyId={matterPropertyId}
                value={matterRoomId}
                onChange={setMatterRoomId}
              />
            )}
            <button
              onClick={startMatterCommission}
              disabled={!matterSetupCode.trim()}
              className="w-full py-2.5 bg-green-600 hover:bg-green-700 disabled:opacity-40 rounded-lg text-sm text-text font-medium transition-colors"
            >
              Commission Device
            </button>
          </div>
        </div>
      );
    }

    if (matterSubView === "commissioning") {
      return (
        <div className="p-6 max-w-md mx-auto">
          <h2 className="text-lg font-bold text-text mb-5">Commissioning Device</h2>
          <div className="bg-surface border border-border rounded-xl p-4 space-y-2 mb-3 min-h-[120px]">
            {commissionLog.map((msg, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-text-2">
                <CheckCircle size={13} className="text-green shrink-0" />
                {msg}
              </div>
            ))}
            <div className="flex items-center gap-2 text-sm text-text-3">
              <Loader2 size={13} className="animate-spin shrink-0" />
              Working...
            </div>
          </div>
          <p className="text-xs text-text-3 text-center">
            Keep your device powered on and nearby.
          </p>
        </div>
      );
    }

    if (matterSubView === "commission-success") {
      const deviceName = commissionedDevice
        ? String(commissionedDevice.name ?? "Matter Device")
        : null;
      const prop = properties.find((p) => p.id === matterPropertyId);

      return (
        <div className="p-6 max-w-md mx-auto">
          <h2 className="text-lg font-bold text-text mb-5">
            {commissionError ? "Commissioning Failed" : "Device Added"}
          </h2>
          {commissionError ? (
            <div className="bg-red-900/30 border border-red-700/40 rounded-xl p-4 mb-4">
              <div className="flex items-start gap-2 text-sm text-red">
                <XCircle size={14} className="shrink-0 mt-0.5" />
                {commissionError}
              </div>
            </div>
          ) : (
            <div className="bg-green-900/20 border border-green-700/30 rounded-xl p-4 mb-4 space-y-1">
              <div className="flex items-center gap-2">
                <CheckCircle size={15} className="text-green shrink-0" />
                <p className="text-sm text-text font-medium">{deviceName}</p>
              </div>
              {prop && <p className="text-xs text-text-2 ml-5">{prop.name}</p>}
            </div>
          )}
          <div className="flex gap-2">
            {commissionError && (
              <button
                onClick={() => setMatterSubView("commission")}
                className="flex-1 py-2.5 bg-green-600 hover:bg-green-700 rounded-lg text-sm text-text font-medium"
              >
                Try Again
              </button>
            )}
            <button
              onClick={() => {
                setMatterSubView("choose");
                setMatterSetupCode("");
                setMatterPropertyId("");
                setMatterRoomId("");
                setCommissionedDevice(null);
                setCommissionError("");
              }}
              className="flex-1 py-2.5 bg-surface-2 hover:bg-gray-600 rounded-lg text-sm text-text-2"
            >
              Done
            </button>
          </div>
        </div>
      );
    }

    if (matterSubView === "scan") {
      return (
        <div className="p-6 max-w-2xl mx-auto">
          <BackButton onClick={() => setMatterSubView("choose")} />
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-lg font-bold text-text">Matter Devices on Network</h2>
              <p className="text-sm text-text-2">Devices already commissioned via mobile app</p>
            </div>
            <button
              onClick={runMatterScan}
              disabled={matterScanning}
              className="flex items-center gap-1.5 text-sm text-green hover:text-green disabled:opacity-50"
            >
              {matterScanning ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
              {matterScanning ? "Scanning..." : "Scan Network"}
            </button>
          </div>

          {matterDevices.length === 0 && !matterScanning && (
            <div className="bg-surface border border-border rounded-xl p-6 text-center">
              <p className="text-text-2 text-sm mb-2">No Matter devices found yet.</p>
              <button
                onClick={runMatterScan}
                className="text-sm text-green hover:text-green"
              >
                Scan now
              </button>
            </div>
          )}

          {matterDevices.length > 0 && (
            <div className="space-y-2">
              {matterDevices.map((d, i) => (
                <div key={i} className="flex items-center justify-between bg-surface border border-border rounded-xl px-4 py-3">
                  <div>
                    <p className="text-sm text-text font-medium">{d.name}</p>
                    <p className="text-xs text-text-3">{d.model}</p>
                  </div>
                  <button
                    onClick={() => setSaveTarget(d)}
                    className="text-sm text-text-2 hover:text-text-2 flex items-center gap-1"
                  >
                    <Plus size={13} /> Add
                  </button>
                </div>
              ))}
            </div>
          )}

          {saveTarget && (
            <SaveDeviceModal
              device={saveTarget}
              properties={properties}
              onSave={(propId, roomId, name) => {
                saveMut.mutate({
                  vendor: saveTarget.vendor,
                  name,
                  model: saveTarget.model,
                  ip: saveTarget.ip,
                  mac: saveTarget.mac,
                  property_id: propId,
                  room_id: roomId || null,
                });
              }}
              onClose={() => setSaveTarget(null)}
            />
          )}
        </div>
      );
    }

    // Matter choose sub-view
    return (
      <div className="p-6 max-w-md mx-auto">
        <BackButton onClick={() => setView("main")} />
        <h2 className="text-lg font-bold text-text mb-1">Matter Device</h2>
        <p className="text-sm text-text-2 mb-5">Choose how to add your Matter device.</p>
        <div className="space-y-3">
          <button
            onClick={() => setMatterSubView("commission")}
            className="w-full flex items-center gap-4 bg-surface border border-border hover:border-border-strong rounded-xl p-4 text-left transition-colors"
          >
            <div className="w-9 h-9 rounded-lg bg-green-bg flex items-center justify-center shrink-0">
              <Smartphone size={18} className="text-green" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-text">Set up a new device</p>
              <p className="text-xs text-text-3">Enter setup code from device packaging</p>
            </div>
            <ChevronRight size={14} className="text-text-3" />
          </button>

          <button
            onClick={() => { setMatterSubView("scan"); runMatterScan(); }}
            className="w-full flex items-center gap-4 bg-surface border border-border hover:border-border-strong rounded-xl p-4 text-left transition-colors"
          >
            <div className="w-9 h-9 rounded-lg bg-blue-500/20 flex items-center justify-center shrink-0">
              <Search size={18} className="text-text-2" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-text">Already set up your device?</p>
              <p className="text-xs text-text-3">Find it on your local network</p>
            </div>
            <ChevronRight size={14} className="text-text-3" />
          </button>
        </div>
      </div>
    );
  }

  // ── Main view ────────────────────────────────────────────────────────────────

  const realDevices = savedDevices.filter((d) => d.vendor !== "demo");

  const shellyConnected = realDevices.some((d) => d.vendor === "shelly");
  const matterConnected = realDevices.some((d) => d.vendor === "matter");
  const goveeConnected = integrations.find((i) => i.vendor === "govee")?.connected ?? false;
  const lifxConnected = integrations.find((i) => i.vendor === "lifx")?.connected ?? false;

  const vendorCards = [
    {
      key: "shelly",
      icon: Wifi,
      iconBg: "bg-amber-bg",
      iconColor: "text-amber",
      name: "Shelly",
      connectionType: "Local network",
      connected: shellyConnected,
      deviceCount: realDevices.filter((d) => d.vendor === "shelly").length,
      onAction: () => setView("hotspot-list"),
    },
    {
      key: "govee",
      icon: Cloud,
      iconBg: "bg-surface-2",
      iconColor: "text-text-2",
      name: "Govee",
      connectionType: "Cloud API",
      connected: goveeConnected,
      deviceCount: realDevices.filter((d) => d.vendor === "govee").length,
      onAction: undefined as (() => void) | undefined,
    },
    {
      key: "lifx",
      icon: Sun,
      iconBg: "bg-surface-2",
      iconColor: "text-text-2",
      name: "LIFX",
      connectionType: "Cloud API",
      connected: lifxConnected,
      deviceCount: realDevices.filter((d) => d.vendor === "lifx").length,
      onAction: undefined as (() => void) | undefined,
    },
    {
      key: "matter",
      icon: Cpu,
      iconBg: "bg-green-bg",
      iconColor: "text-green",
      name: "Matter",
      connectionType: "Matter protocol",
      connected: matterConnected,
      deviceCount: realDevices.filter((d) => d.vendor === "matter").length,
      onAction: () => { setView("matter"); setMatterSubView("choose"); },
    },
  ];

  return (
    <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-10">
      <div>
        <h1 className="font-display italic text-2xl text-text">Integrations</h1>
        <p className="font-body font-light text-sm text-text-3 mt-1">Manage vendor connections and add devices</p>
      </div>

      {/* Section 1: Connected hardware summary */}
      <section>
        <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-4">
          Connected Hardware
        </p>
        {devicesLoading ? (
          <div className="h-24 bg-surface border border-border rounded-xl animate-pulse" />
        ) : (
          <div className="bg-surface border border-border rounded-xl p-5 flex items-start justify-between gap-4">
            <div>
              <p className="font-display italic text-3xl text-text leading-none">{realDevices.length}</p>
              <p className="font-body font-light text-sm text-text-3 mt-1">
                physical device{realDevices.length !== 1 ? "s" : ""} connected
              </p>
              {realDevices.length > 0 && (
                <p className="font-mono text-xs text-text-3 mt-2.5">
                  {realDevices.slice(0, 3).map((d) => d.name).join(" · ")}
                  {realDevices.length > 3 ? ` · +${realDevices.length - 3} more` : ""}
                </p>
              )}
            </div>
            <Link
              href="/devices"
              className="flex items-center gap-1 font-body font-light text-xs text-text-3 hover:text-text-2 transition-colors shrink-0 mt-1"
            >
              View all devices <ChevronRight size={11} />
            </Link>
          </div>
        )}
      </section>

      {/* Section 2: Vendor connections */}
      <section>
        <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-4">
          Vendor Connections
        </p>
        <div className="space-y-3">
          {vendorCards.map(({ key, icon: Icon, iconBg, iconColor, name, connectionType, connected, deviceCount, onAction }) => (
            <div
              key={key}
              className="bg-surface border border-border rounded-xl px-5 py-4 flex items-center gap-4"
            >
              <div className={`w-10 h-10 rounded-lg ${iconBg} flex items-center justify-center shrink-0`}>
                <Icon size={17} className={iconColor} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-body font-normal text-sm text-text">{name}</p>
                  <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${connected ? "bg-green" : "bg-border"}`} />
                  <span className={`font-mono text-xs ${connected ? "text-green" : "text-text-3"}`}>
                    {connected ? "Connected" : "Not connected"}
                  </span>
                </div>
                <p className="font-mono text-xs text-text-3 mt-0.5">
                  {connectionType} · {deviceCount} device{deviceCount !== 1 ? "s" : ""}
                </p>
              </div>
              <button
                onClick={onAction}
                disabled={!onAction}
                className="font-body font-light text-xs px-3 py-1.5 rounded-lg border border-border text-text-3 hover:border-border-strong hover:text-text-2 transition-colors shrink-0 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {connected ? "Manage" : "Connect"}
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Section 3: Add a device */}
      <section>
        <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-4">
          Add a Device
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            {
              icon: Wifi,
              title: "Set Up New Device",
              desc: "Connect a new Shelly device via its hotspot",
              iconBg: "bg-amber-bg",
              iconColor: "text-amber",
              onClick: () => setView("hotspot-list"),
            },
            {
              icon: Search,
              title: "Find on Network",
              desc: "Discover devices already on your local WiFi",
              iconBg: "bg-surface-2",
              iconColor: "text-text-2",
              onClick: () => setView("scan-network"),
            },
            {
              icon: Smartphone,
              title: "Matter Device",
              desc: "Commission a Matter-compatible smart device",
              iconBg: "bg-green-bg",
              iconColor: "text-green",
              onClick: () => { setView("matter"); setMatterSubView("choose"); },
            },
          ].map(({ icon: Icon, title, desc, iconBg, iconColor, onClick }) => (
            <motion.button
              key={title}
              onClick={onClick}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
              className="bg-surface border border-border rounded-xl p-5 text-left hover:border-border-strong transition-colors"
            >
              <div className={`w-12 h-12 rounded-full ${iconBg} flex items-center justify-center mb-4`}>
                <Icon size={20} className={iconColor} />
              </div>
              <p className="font-body font-normal text-sm text-text mb-1">{title}</p>
              <p className="font-body font-light text-xs text-text-3 leading-relaxed">{desc}</p>
              <p className="font-body font-light text-xs text-text-2 mt-3">Start →</p>
            </motion.button>
          ))}
        </div>
      </section>

      {/* Section 4: Coming soon vendors */}
      <section>
        <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-4">
          Coming Soon
        </p>
        <div className="flex flex-wrap gap-2">
          {["Zigbee", "Z-Wave", "HomeKit", "Tuya", "Tasmota"].map((label) => (
            <span
              key={label}
              className="inline-flex items-center gap-1.5 font-mono text-xs px-3 py-1.5 rounded-full border border-border bg-surface-2 text-text-3 opacity-50"
            >
              {label}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}

// Inject pulse animation
if (typeof document !== "undefined") {
  const style = document.createElement("style");
  style.textContent = `@keyframes pulse-dot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(1.4)} }`;
  if (!document.head.querySelector("[data-pulse-dot]")) {
    style.setAttribute("data-pulse-dot", "1");
    document.head.appendChild(style);
  }
}
