"use client";

import { useEffect, useRef, useState } from "react";
import {
  type ActivityEntry,
  type DemoDevice,
  formatRelativeTime,
} from "./types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function protocolLabel(device: DemoDevice): string {
  if (device.model === "ble") return "Bluetooth";
  if (device.provider === "lifx") return "Wi-Fi";
  return "Cloud";
}

function providerLabel(provider: DemoDevice["provider"]): string {
  return provider === "lifx" ? "LIFX" : "Govee";
}

export default function DemoPage() {
  const [devices, setDevices] = useState<DemoDevice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activity, setActivity] = useState<ActivityEntry[]>([]);
  const [busy, setBusy] = useState<Set<string>>(new Set());
  const ticker = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    loadDevices();
    ticker.current = setInterval(() => setActivity((a) => [...a]), 10_000);
    return () => {
      if (ticker.current) clearInterval(ticker.current);
    };
  }, []);

  async function loadDevices() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/demo/devices`);
      if (!res.ok) throw new Error(`${res.status}`);
      setDevices(await res.json());
    } catch {
      setError("Could not reach the backend. Is it running on port 8000?");
    } finally {
      setLoading(false);
    }
  }

  function addActivity(message: string) {
    setActivity((prev) => [
      { id: crypto.randomUUID(), message, time: new Date() },
      ...prev.slice(0, 9),
    ]);
  }

  function markBusy(id: string, on: boolean) {
    setBusy((prev) => {
      const next = new Set(prev);
      if (on) {
        next.add(id);
      } else {
        next.delete(id);
      }
      return next;
    });
  }

  async function togglePower(device: DemoDevice) {
    const next = !device.power;
    const key = device.id;
    markBusy(key, true);
    setDevices((prev) =>
      prev.map((d) => (d.id === key ? { ...d, power: next } : d)),
    );
    try {
      const url =
        device.provider === "govee"
          ? `${API}/demo/devices/govee/${encodeURIComponent(key)}/power?model=${encodeURIComponent(device.model ?? "")}`
          : `${API}/demo/devices/lifx/${encodeURIComponent(key)}/power`;
      await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ on: next }),
      });
      addActivity(`${device.name} turned ${next ? "on" : "off"}`);
    } catch {
      setDevices((prev) =>
        prev.map((d) => (d.id === key ? { ...d, power: device.power } : d)),
      );
    } finally {
      markBusy(key, false);
    }
  }

  async function changeBrightness(device: DemoDevice, brightness: number) {
    const key = device.id;
    setDevices((prev) =>
      prev.map((d) => (d.id === key ? { ...d, brightness } : d)),
    );
    try {
      await fetch(
        `${API}/demo/devices/lifx/${encodeURIComponent(key)}/brightness`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ brightness }),
        },
      );
      addActivity(
        `${device.name} brightness → ${Math.round(brightness * 100)}%`,
      );
    } catch {
      // best-effort
    }
  }

  const reachable = devices.filter((d) => d.reachable).length;

  return (
    <>
      {/* Page header */}
      <div className="mb-8">
        <h1 className="font-serif text-[26px] leading-[1.2] text-text tracking-tight">
          Smart device control
        </h1>
        <p className="font-mono text-[11px] uppercase tracking-[0.08em] text-text-3 mt-1.5">
          {loading
            ? "Loading…"
            : `${reachable} of ${devices.length} device${devices.length !== 1 ? "s" : ""} reachable`}
        </p>
      </div>

      {/* Error state */}
      {error && (
        <div className="mb-6 rounded-card border border-red/20 bg-red-bg px-4 py-3 text-[13px] text-red">
          {error}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && devices.length === 0 && (
        <div className="rounded-card border border-border bg-surface px-5 py-10 text-center">
          <p className="text-[13px] text-text-2">No devices found.</p>
          <p className="text-[12px] text-text-3 mt-1">
            Add your API keys to{" "}
            <code className="font-mono text-[11px] text-text-2">
              backend/.env
            </code>{" "}
            and restart the server.
          </p>
        </div>
      )}

      {/* Device grid */}
      {devices.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-10">
          {devices.map((device) => (
            <DeviceCard
              key={`${device.provider}-${device.id}`}
              device={device}
              isBusy={busy.has(device.id)}
              onToggle={() => togglePower(device)}
              onBrightness={(b) => changeBrightness(device, b)}
            />
          ))}
        </div>
      )}

      {/* Activity feed */}
      {activity.length > 0 && (
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 mb-3">
            Activity
          </p>
          <div className="rounded-card border border-border bg-surface divide-y divide-border">
            {activity.map((entry) => (
              <div
                key={entry.id}
                className="flex items-baseline gap-2 px-4 py-2.5"
              >
                <span className="text-[13px] text-text-2 flex-1">
                  {entry.message}
                </span>
                <span className="font-mono text-[10px] text-text-3 shrink-0">
                  {formatRelativeTime(entry.time)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

interface CardProps {
  device: DemoDevice;
  isBusy: boolean;
  onToggle: () => void;
  onBrightness: (b: number) => void;
}

function DeviceCard({ device, isBusy, onToggle, onBrightness }: CardProps) {
  const offline = !device.reachable;
  const protocol = protocolLabel(device);

  return (
    <div
      className={`rounded-card border bg-surface p-5 flex flex-col gap-4 transition-opacity duration-200 ${
        offline
          ? "opacity-50 border-border"
          : "border-border hover:border-border-strong"
      }`}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="text-[14px] font-semibold text-text leading-snug truncate">
            {device.name}
          </p>
          <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
            {/* Provider badge */}
            <span className="font-mono text-[10px] uppercase tracking-[0.08em] px-2 py-0.5 rounded-tag bg-surface-2 text-text-2 border border-border">
              {providerLabel(device.provider)}
            </span>
            {/* Protocol badge */}
            <span
              className={`font-mono text-[10px] uppercase tracking-[0.08em] px-2 py-0.5 rounded-tag ${
                protocol === "Bluetooth"
                  ? "bg-green-bg text-green border border-green/20"
                  : protocol === "Wi-Fi"
                    ? "bg-amber-bg text-amber border border-amber/20"
                    : "bg-surface-2 text-text-2 border border-border"
              }`}
            >
              {protocol}
            </span>
          </div>
        </div>

        {/* Status dot */}
        <div className="shrink-0 mt-0.5">
          <span className="sr-only">{offline ? "Offline" : "Online"}</span>
          <div
            className={`w-2 h-2 rounded-full ${offline ? "bg-red" : device.power ? "bg-green" : "bg-text-3"}`}
          />
        </div>
      </div>

      {/* Power toggle */}
      <div className="flex items-center justify-between">
        <span className="text-[12px] text-text-3">
          {offline ? "Offline" : device.power ? "On" : "Off"}
        </span>
        <button
          onClick={onToggle}
          disabled={isBusy || offline}
          aria-label={`Turn ${device.name} ${device.power ? "off" : "on"}`}
          className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-graphite focus:ring-offset-2 focus:ring-offset-bg disabled:cursor-not-allowed disabled:opacity-40 ${
            device.power ? "bg-graphite" : "bg-surface-2"
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow-sm ring-0 transition-transform duration-200 ${
              device.power ? "translate-x-5" : "translate-x-0"
            }`}
          />
        </button>
      </div>

      {/* LIFX brightness slider */}
      {device.provider === "lifx" &&
        device.brightness !== null &&
        device.power && (
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[12px] text-text-3">Brightness</span>
              <span className="font-mono text-[10px] text-text-3">
                {Math.round((device.brightness ?? 0) * 100)}%
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={device.brightness ?? 0}
              disabled={offline}
              onChange={(e) => onBrightness(parseFloat(e.target.value))}
              className="w-full accent-graphite disabled:opacity-40"
            />
          </div>
        )}
    </div>
  );
}
