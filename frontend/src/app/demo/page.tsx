"use client";

import { useEffect, useRef, useState } from "react";
import {
  type ActivityEntry,
  type DemoDevice,
  formatRelativeTime,
  providerLabel,
} from "./types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const PROVIDER_STYLES: Record<DemoDevice["provider"], string> = {
  lifx: "bg-purple-900/40 text-purple-300 border border-purple-800",
  govee: "bg-teal-900/40 text-teal-300 border border-teal-800",
};

export default function DemoPage() {
  const [devices, setDevices] = useState<DemoDevice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activity, setActivity] = useState<ActivityEntry[]>([]);
  const [busy, setBusy] = useState<Set<string>>(new Set());
  const ticker = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    loadDevices();
    // Re-render activity timestamps every 10s
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

  const connected = devices.filter((d) => d.reachable).length;

  return (
    <>
      <div className="mb-8">
        <h1 className="text-xl font-semibold mb-1">Smart device control</h1>
        <p className="text-sm text-gray-400">
          {loading
            ? "Loading…"
            : `${connected} of ${devices.length} device${devices.length !== 1 ? "s" : ""} reachable`}
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-800 bg-red-900/20 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {!loading && !error && devices.length === 0 && (
        <p className="text-gray-400 text-sm">
          No devices found. Add your API keys to{" "}
          <code className="text-gray-300">backend/.env</code> and restart the
          server.
        </p>
      )}

      {devices.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
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

      {activity.length > 0 && (
        <div>
          <p className="text-xs font-medium uppercase tracking-widest text-gray-500 mb-3">
            Activity
          </p>
          <ul className="space-y-2">
            {activity.map((entry) => (
              <li key={entry.id} className="flex items-baseline gap-2 text-sm">
                <span className="text-gray-600">·</span>
                <span className="text-gray-300">{entry.message}</span>
                <span className="text-gray-600 text-xs ml-auto shrink-0">
                  {formatRelativeTime(entry.time)}
                </span>
              </li>
            ))}
          </ul>
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

  return (
    <div
      className={`rounded-xl border p-5 flex flex-col gap-4 transition-opacity ${
        offline
          ? "opacity-40 border-gray-800 bg-gray-900/40"
          : "border-gray-700 bg-gray-900"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="font-medium text-sm truncate">{device.name}</p>
          {offline && <p className="text-xs text-gray-500 mt-0.5">Offline</p>}
        </div>
        <span
          className={`shrink-0 text-xs px-2 py-0.5 rounded-full font-medium ${PROVIDER_STYLES[device.provider]}`}
        >
          {providerLabel(device.provider)}
        </span>
      </div>

      <button
        onClick={onToggle}
        disabled={isBusy || offline}
        aria-label={`Turn ${device.name} ${device.power ? "off" : "on"}`}
        className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none disabled:cursor-not-allowed ${
          device.power ? "bg-green-500" : "bg-gray-700"
        }`}
      >
        <span
          className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow ring-0 transition-transform duration-200 ${
            device.power ? "translate-x-5" : "translate-x-0"
          }`}
        />
      </button>

      {device.provider === "lifx" &&
        device.brightness !== null &&
        device.power && (
          <div className="flex flex-col gap-1.5">
            <p className="text-xs text-gray-400">
              Brightness · {Math.round((device.brightness ?? 0) * 100)}%
            </p>
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={device.brightness ?? 0}
              disabled={offline}
              onChange={(e) => onBrightness(parseFloat(e.target.value))}
              className="w-full accent-purple-400 disabled:opacity-40"
            />
          </div>
        )}
    </div>
  );
}
