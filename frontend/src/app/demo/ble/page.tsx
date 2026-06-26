"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface ScannedDevice {
  address: string;
  name: string;
  device_type: "light" | "speaker" | "phone" | "unknown";
  rssi: number | null;
}

interface Characteristic {
  uuid: string;
  properties: string[];
}

interface Service {
  uuid: string;
  characteristics: Characteristic[];
}

interface ProbeResult {
  address: string;
  name: string;
  device_type: string;
  connectable: boolean;
  services: Service[];
  error: string | null;
}

function signalLabel(rssi: number | null): string {
  if (rssi === null) return "–";
  if (rssi >= -60) return "Strong";
  if (rssi >= -75) return "Good";
  if (rssi >= -85) return "Weak";
  return "Poor";
}

function signalStyle(rssi: number | null): string {
  if (rssi === null) return "text-text-3";
  if (rssi >= -60) return "text-green";
  if (rssi >= -75) return "text-text-2";
  if (rssi >= -85) return "text-amber";
  return "text-red";
}

const TYPE_LABELS: Record<string, string> = {
  light: "Light",
  speaker: "Speaker",
  phone: "Phone",
  unknown: "Unknown",
};

const TYPE_STYLES: Record<string, string> = {
  light: "bg-amber-bg text-amber border border-amber/20",
  speaker: "bg-green-bg text-green border border-green/20",
  phone: "bg-surface-2 text-text-2 border border-border",
  unknown: "bg-surface-2 text-text-3 border border-border",
};

export default function BLEScannerPage() {
  const [scanning, setScanning] = useState(false);
  const [devices, setDevices] = useState<ScannedDevice[]>([]);
  const [scanned, setScanned] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [probing, setProbing] = useState<string | null>(null);
  const [probeResult, setProbeResult] = useState<ProbeResult | null>(null);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  async function runScan() {
    setScanning(true);
    setError(null);
    setDevices([]);
    setProbeResult(null);
    try {
      const res = await fetch(`${API}/demo/ble/scan`);
      if (!res.ok) throw new Error(`${res.status}`);
      const data: ScannedDevice[] = await res.json();
      setDevices(data);
      setScanned(true);
    } catch {
      setError(
        "Scan failed. Make sure the backend is running and Bluetooth is enabled.",
      );
    } finally {
      setScanning(false);
    }
  }

  async function runProbe(address: string) {
    setProbing(address);
    setProbeResult(null);
    try {
      const res = await fetch(
        `${API}/demo/ble/${encodeURIComponent(address)}/probe`,
        {
          method: "POST",
        },
      );
      if (!res.ok) throw new Error(`${res.status}`);
      setProbeResult(await res.json());
    } catch {
      setProbeResult({
        address,
        name: "Unknown",
        device_type: "unknown",
        connectable: false,
        services: [],
        error: "Could not reach the backend.",
      });
    } finally {
      setProbing(null);
    }
  }

  function toggleExpand(uuid: string) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(uuid)) {
        next.delete(uuid);
      } else {
        next.add(uuid);
      }
      return next;
    });
  }

  const grouped = {
    light: devices.filter((d) => d.device_type === "light"),
    speaker: devices.filter((d) => d.device_type === "speaker"),
    phone: devices.filter((d) => d.device_type === "phone"),
    unknown: devices.filter((d) => d.device_type === "unknown"),
  };

  return (
    <>
      {/* Page header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="font-serif text-[26px] leading-[1.2] text-text tracking-tight">
            Bluetooth scanner
          </h1>
          <p className="font-mono text-[11px] uppercase tracking-[0.08em] text-text-3 mt-1.5">
            {scanning
              ? "Scanning nearby devices…"
              : scanned
                ? `${devices.length} device${devices.length !== 1 ? "s" : ""} found`
                : "Discover and probe nearby BLE devices"}
          </p>
        </div>
        <button
          onClick={runScan}
          disabled={scanning}
          className="bg-graphite text-white text-[13px] font-medium px-4 py-2 rounded-input hover:bg-graphite-2 disabled:opacity-40 transition-colors duration-120"
        >
          {scanning ? "Scanning…" : "Scan"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 rounded-card border border-red/20 bg-red-bg px-4 py-3 text-[13px] text-red">
          {error}
        </div>
      )}

      {/* Scanning indicator */}
      {scanning && (
        <div className="rounded-card border border-border bg-surface px-5 py-10 text-center mb-6">
          <p className="text-[13px] text-text-2">Scanning up to 8 seconds…</p>
          <p className="text-[12px] text-text-3 mt-1">
            Keep nearby devices powered on
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Device list */}
        {scanned && !scanning && (
          <div>
            {devices.length === 0 ? (
              <div className="rounded-card border border-border bg-surface px-5 py-10 text-center">
                <p className="text-[13px] text-text-2">
                  No named devices found.
                </p>
                <p className="text-[12px] text-text-3 mt-1">
                  Ensure devices are powered on and within range.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {(["light", "speaker", "phone", "unknown"] as const).map(
                  (type) =>
                    grouped[type].length > 0 ? (
                      <div key={type}>
                        <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 mb-2">
                          {TYPE_LABELS[type]}s
                        </p>
                        <div className="rounded-card border border-border bg-surface divide-y divide-border">
                          {grouped[type].map((device) => (
                            <div
                              key={device.address}
                              className="flex items-center gap-3 px-4 py-3"
                            >
                              <div className="flex-1 min-w-0">
                                <p className="text-[13px] font-medium text-text truncate">
                                  {device.name}
                                </p>
                                <p className="font-mono text-[10px] text-text-3 mt-0.5 truncate">
                                  {device.address}
                                </p>
                              </div>
                              <span
                                className={`shrink-0 font-mono text-[10px] uppercase tracking-[0.08em] px-2 py-0.5 rounded-tag ${TYPE_STYLES[device.device_type]}`}
                              >
                                {TYPE_LABELS[device.device_type]}
                              </span>
                              <span
                                className={`shrink-0 font-mono text-[10px] ${signalStyle(device.rssi)}`}
                                title={
                                  device.rssi !== null
                                    ? `${device.rssi} dBm`
                                    : "No signal data"
                                }
                              >
                                {signalLabel(device.rssi)}
                              </span>
                              <button
                                onClick={() => runProbe(device.address)}
                                disabled={probing === device.address}
                                className="shrink-0 text-[12px] font-medium text-text-2 bg-surface-2 border border-border px-3 py-1.5 rounded-input hover:bg-bg hover:border-border-strong disabled:opacity-40 transition-colors duration-120"
                              >
                                {probing === device.address
                                  ? "Probing…"
                                  : "Probe"}
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null,
                )}
              </div>
            )}
          </div>
        )}

        {/* Probe result panel */}
        {probeResult && (
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 mb-2">
              Probe result
            </p>
            <div className="rounded-card border border-border bg-surface p-5">
              {/* Device identity */}
              <div className="flex items-start justify-between gap-3 mb-4">
                <div>
                  <p className="text-[14px] font-semibold text-text">
                    {probeResult.name}
                  </p>
                  <p className="font-mono text-[10px] text-text-3 mt-0.5">
                    {probeResult.address}
                  </p>
                </div>
                <span
                  className={`shrink-0 font-mono text-[10px] uppercase tracking-[0.08em] px-2 py-0.5 rounded-tag ${
                    probeResult.connectable
                      ? "bg-green-bg text-green border border-green/20"
                      : "bg-red-bg text-red border border-red/20"
                  }`}
                >
                  {probeResult.connectable ? "Connected" : "Unreachable"}
                </span>
              </div>

              {/* Error */}
              {probeResult.error && (
                <p className="text-[12px] text-text-2 bg-surface-2 border border-border rounded-input px-3 py-2 mb-4">
                  {probeResult.error}
                </p>
              )}

              {/* Services */}
              {probeResult.services.length > 0 && (
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 mb-2">
                    {probeResult.services.length} service
                    {probeResult.services.length !== 1 ? "s" : ""} discovered
                  </p>
                  <div className="space-y-1">
                    {probeResult.services.map((svc) => (
                      <div
                        key={svc.uuid}
                        className="border border-border rounded-input overflow-hidden"
                      >
                        <button
                          onClick={() => toggleExpand(svc.uuid)}
                          className="w-full flex items-center justify-between px-3 py-2 bg-surface-2 hover:bg-bg text-left transition-colors duration-120"
                        >
                          <span className="font-mono text-[10px] text-text-2 truncate pr-2">
                            {svc.uuid}
                          </span>
                          <span className="font-mono text-[10px] text-text-3 shrink-0">
                            {expanded.has(svc.uuid) ? "▲" : "▼"}{" "}
                            {svc.characteristics.length}
                          </span>
                        </button>
                        {expanded.has(svc.uuid) && (
                          <div className="divide-y divide-border">
                            {svc.characteristics.map((char) => (
                              <div
                                key={char.uuid}
                                className="px-3 py-2 flex items-start gap-3"
                              >
                                <span className="font-mono text-[10px] text-text-2 flex-1 truncate">
                                  {char.uuid}
                                </span>
                                <div className="flex gap-1 flex-wrap justify-end">
                                  {char.properties.map((p) => (
                                    <span
                                      key={p}
                                      className="font-mono text-[9px] uppercase tracking-[0.06em] px-1.5 py-0.5 rounded bg-surface-2 text-text-3 border border-border"
                                    >
                                      {p}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
