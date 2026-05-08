"use client";

import { use, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Activity,
  ArrowLeft,
  Battery,
  Gauge,
  MoreHorizontal,
  Power,
  RefreshCw,
  Trash2,
  Zap,
  X,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { DeviceStateHistory } from "@/components/device/DeviceStateHistory";
import { DeviceControls } from "@/components/device/DeviceControls";
import { useDevice } from "@/hooks/useDevices";
import { useProperty } from "@/hooks/useProperty";
import { matterApi, shellyDeviceApi, roomsApi } from "@/lib/api";
import type {
  MatterDeviceState,
  PowerHistoryPoint,
  ShellyDeviceState,
} from "@/lib/types";
import { cn } from "@/lib/utils";

// ── Vendor badge ──────────────────────────────────────────────────────────────

const VENDOR_COLOURS: Record<string, string> = {
  shelly: "bg-amber-bg text-amber border-amber/20",
  matter: "bg-green-bg text-green border-green/20",
  govee: "bg-surface-2 text-text-2 border-border",
  lifx: "bg-surface-2 text-text-2 border-border",
  demo: "bg-surface-2 text-text-3 border-border",
};

function VendorBadge({ vendor }: { vendor: string }) {
  const cls = VENDOR_COLOURS[vendor.toLowerCase()] ?? "bg-surface-2 text-text-3 border-border";
  return (
    <span className={`inline-flex items-center font-mono text-xs px-2 py-0.5 rounded-full capitalize border ${cls}`}>
      {vendor}
    </span>
  );
}

// ── Metric card ───────────────────────────────────────────────────────────────

function MetricCard({
  icon: Icon,
  label,
  value,
  unit,
  highlight,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  unit: string;
  highlight?: boolean;
}) {
  return (
    <div className="bg-surface-2 border border-border rounded-xl p-4 flex flex-col gap-2">
      <div className="flex items-center gap-1.5 text-text-3">
        <Icon size={13} />
        <span className="font-body font-normal text-xs uppercase tracking-wide">{label}</span>
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className={`font-mono text-2xl tabular-nums ${highlight ? "text-amber" : "text-text"}`}>
          {value}
        </span>
        <span className="font-mono text-xs text-text-3">{unit}</span>
      </div>
    </div>
  );
}

// ── Power chart tooltip ───────────────────────────────────────────────────────

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { value: number }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface border border-border rounded-lg px-3 py-2 text-xs">
      <p className="font-mono text-text-3 mb-0.5">{label}</p>
      <p className="font-mono text-text font-medium">{payload[0].value.toFixed(1)} W</p>
    </div>
  );
}

// ── Delete confirmation dialog ────────────────────────────────────────────────

function DeleteDialog({
  deviceName,
  onCancel,
  onConfirm,
  isPending,
}: {
  deviceName: string;
  onCancel: () => void;
  onConfirm: () => void;
  isPending: boolean;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-graphite/30 backdrop-blur-sm"
        onClick={onCancel}
      />
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.15 }}
        className="relative w-full max-w-sm bg-surface border border-border rounded-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <p className="font-body font-normal text-sm text-text">Delete {deviceName}?</p>
          <button onClick={onCancel} className="text-text-3 hover:text-text-2 transition-colors">
            <X size={14} />
          </button>
        </div>
        <div className="px-5 py-5">
          <p className="font-body font-light text-sm text-text-2 leading-relaxed">
            This will remove the device and all its history from your portfolio. This cannot be undone.
          </p>
        </div>
        <div className="px-5 py-4 border-t border-border flex items-center justify-end gap-3">
          <button
            onClick={onCancel}
            className="font-body font-light text-sm text-text-3 hover:text-text-2 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isPending}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red text-surface text-sm font-body transition-colors hover:opacity-90 disabled:opacity-50"
          >
            {isPending ? (
              <span className="w-3 h-3 border border-surface/40 border-t-surface rounded-full animate-spin" />
            ) : (
              <Trash2 size={13} />
            )}
            Delete device
          </button>
        </div>
      </motion.div>
    </div>
  );
}

// ── Shelly panel (live readings + controls) ───────────────────────────────────

function ShellyPanel({
  deviceId,
  deviceName,
  onOnlineResolved,
}: {
  deviceId: string;
  deviceName: string;
  onOnlineResolved?: (online: boolean) => void;
}) {
  const queryClient = useQueryClient();

  const {
    data: state,
    isLoading,
    isError,
    refetch,
    isRefetching,
  } = useQuery<ShellyDeviceState>({
    queryKey: ["shelly-state", deviceId],
    queryFn: async () => {
      const result = await shellyDeviceApi.getState(deviceId);
      onOnlineResolved?.(result?.online ?? true);
      return result;
    },
    refetchInterval: 10_000,
    retry: false,
  });

  const { data: history = [] } = useQuery<PowerHistoryPoint[]>({
    queryKey: ["shelly-power-history", deviceId],
    queryFn: () => shellyDeviceApi.getPowerHistory(deviceId),
    refetchInterval: 60_000,
    retry: false,
  });

  const controlMut = useMutation({
    mutationFn: (command: "turn_on" | "turn_off") =>
      shellyDeviceApi.control(deviceId, command),
    onSuccess: (_data, command) => {
      const action = command === "turn_on" ? "on" : "off";
      toast.success(`${deviceName} turned ${action}`);
      refetch();
      queryClient.invalidateQueries({ queryKey: ["shelly-state", deviceId] });
    },
    onError: () => {
      toast.error("Failed to reach device. Check it is on your local network.");
    },
  });

  const isOn = state?.on ?? false;

  const chartData = (() => {
    if (!history.length) return [];
    const step = Math.max(1, Math.floor(history.length / 144));
    return history
      .filter((_, i) => i % step === 0)
      .map((p) => ({
        time: new Date(p.recorded_at).toLocaleTimeString(undefined, {
          timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          hour: "2-digit",
          minute: "2-digit",
        }),
        watts: parseFloat(p.value),
      }));
  })();

  return (
    <div className="space-y-4">
      {/* Live readings */}
      <div className="bg-surface border border-border rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-body font-normal text-sm text-text">Live Readings</h3>
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="p-1.5 text-text-3 hover:text-text-2 transition-colors disabled:opacity-40"
            title="Refresh"
          >
            <RefreshCw size={13} className={isRefetching ? "animate-spin" : ""} />
          </button>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-2 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-surface-2 border border-border rounded-xl h-20 animate-pulse" />
            ))}
          </div>
        ) : isError ? (
          <p className="font-body font-light text-xs text-red">
            Could not reach device — check it is powered on and reachable on your local network.
          </p>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            <MetricCard icon={Zap} label="Power" value={(state?.power ?? 0).toFixed(1)} unit="W" highlight={(state?.power ?? 0) > 0} />
            <MetricCard icon={Activity} label="Voltage" value={(state?.voltage ?? 0).toFixed(1)} unit="V" />
            <MetricCard icon={Gauge} label="Current" value={(state?.current ?? 0).toFixed(2)} unit="A" />
            <MetricCard icon={Battery} label="Today" value={(state?.energy ?? 0).toFixed(0)} unit="Wh" />
          </div>
        )}
      </div>

      {/* Controls — always visible for Shelly */}
      <div className="bg-surface border border-border rounded-xl p-5">
        <h3 className="font-body font-normal text-sm text-text mb-4">Controls</h3>
        <div className="flex items-center justify-between">
          <div>
            <span className="font-body font-light text-sm text-text-2">Power</span>
            {state && (state.power ?? 0) > 0 && (
              <span className="ml-2 font-mono text-xs text-text-3">{state.power.toFixed(1)} W</span>
            )}
          </div>
          <button
            onClick={() => controlMut.mutate(isOn ? "turn_off" : "turn_on")}
            disabled={controlMut.isPending || isLoading}
            className={cn(
              "flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-body transition-all disabled:opacity-50",
              isOn
                ? "bg-green text-surface hover:opacity-90"
                : "bg-graphite text-surface hover:bg-graphite-2"
            )}
          >
            {controlMut.isPending ? (
              <span className="w-3 h-3 border border-surface/40 border-t-surface rounded-full animate-spin" />
            ) : (
              <Power size={15} />
            )}
            {controlMut.isPending ? "Sending…" : isOn ? "Turn Off" : "Turn On"}
          </button>
        </div>
      </div>

      {/* Power chart */}
      {chartData.length > 1 && (
        <div className="bg-surface border border-border rounded-xl p-5">
          <p className="font-body font-normal text-sm text-text mb-4">Power — last 24 h</p>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="powerGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#9a5e15" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#9a5e15" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0dbcf" vertical={false} />
                <XAxis
                  dataKey="time"
                  tick={{ fill: "#a39d8e", fontSize: 10, fontFamily: "var(--font-dm-mono)" }}
                  tickLine={false}
                  axisLine={false}
                  interval="preserveStartEnd"
                />
                <YAxis
                  tick={{ fill: "#a39d8e", fontSize: 10, fontFamily: "var(--font-dm-mono)" }}
                  tickLine={false}
                  axisLine={false}
                  unit="W"
                />
                <Tooltip content={<ChartTooltip />} />
                <Area
                  type="monotone"
                  dataKey="watts"
                  stroke="#9a5e15"
                  strokeWidth={1.5}
                  fill="url(#powerGrad)"
                  dot={false}
                  activeDot={{ r: 3, fill: "#9a5e15" }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Matter control panel ──────────────────────────────────────────────────────

function MatterControls({ deviceId }: { deviceId: string }) {
  const [brightness, setBrightness] = useState<number>(254);

  const {
    data: state,
    isLoading: stateLoading,
    refetch,
    isRefetching,
  } = useQuery<MatterDeviceState>({
    queryKey: ["matter-state", deviceId],
    queryFn: () => matterApi.getState(deviceId),
    retry: false,
  });

  const onOffMut = useMutation({
    mutationFn: (value: boolean) => matterApi.command(deviceId, "on_off", value),
    onSuccess: () => refetch(),
  });

  const brightnessMut = useMutation({
    mutationFn: (value: number) => matterApi.command(deviceId, "brightness", value),
    onSuccess: () => refetch(),
  });

  if (stateLoading) {
    return (
      <div className="bg-surface border border-border rounded-xl p-5">
        <div className="h-3 w-24 bg-surface-2 rounded animate-pulse mb-4" />
        <div className="space-y-3">
          <div className="h-10 bg-surface-2 rounded animate-pulse" />
          <div className="h-10 bg-surface-2 rounded animate-pulse" />
        </div>
      </div>
    );
  }

  const isOn = state?.on_off ?? false;
  const currentBrightness = state?.brightness ?? brightness;

  return (
    <div className="bg-surface border border-border rounded-xl p-5 space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="font-body font-normal text-sm text-text">Controls</h3>
        <div className="flex items-center gap-2">
          {state && (
            <span className={`font-mono text-xs ${state.online ? "text-green" : "text-text-3"}`}>
              {state.online ? "Online" : "Offline"}
            </span>
          )}
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="p-1.5 text-text-3 hover:text-text-2 transition-colors disabled:opacity-40"
          >
            <RefreshCw size={13} className={isRefetching ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <span className="font-body font-light text-sm text-text-2">Power</span>
        <button
          onClick={() => onOffMut.mutate(!isOn)}
          disabled={onOffMut.isPending}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-body transition-colors disabled:opacity-50",
            isOn
              ? "bg-green text-surface hover:opacity-90"
              : "bg-graphite text-surface hover:bg-graphite-2"
          )}
        >
          <Power size={14} />
          {isOn ? "Turn Off" : "Turn On"}
        </button>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="font-body font-light text-sm text-text-2">Brightness</span>
          <span className="font-mono text-xs text-text-3">
            {Math.round((currentBrightness / 254) * 100)}%
          </span>
        </div>
        <input
          type="range"
          min={0}
          max={254}
          value={currentBrightness}
          onChange={(e) => setBrightness(Number(e.target.value))}
          onMouseUp={(e) => brightnessMut.mutate(Number((e.target as HTMLInputElement).value))}
          onTouchEnd={(e) => brightnessMut.mutate(Number((e.target as HTMLInputElement).value))}
          disabled={brightnessMut.isPending}
          className="w-full disabled:opacity-50"
        />
      </div>

      {(onOffMut.isError || brightnessMut.isError) && (
        <p className="font-body font-light text-xs text-red">
          Command failed — check that the device is online and reachable.
        </p>
      )}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function DeviceDetailPage({
  params,
}: {
  params: Promise<{ id: string; deviceId: string }>;
}) {
  const { id, deviceId } = use(params);
  const router = useRouter();
  const { data: device, isLoading } = useDevice(deviceId);
  const { data: property } = useProperty(id);
  const { data: rooms = [] } = useQuery({
    queryKey: ["rooms", id],
    queryFn: () => roomsApi.list(id),
    enabled: Boolean(id),
  });

  const [liveOnline, setLiveOnline] = useState<boolean | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const room = device?.room_id ? rooms.find((r) => r.id === device.room_id) : null;

  const deleteMut = useMutation({
    mutationFn: () => {
      return fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/devices/${deviceId}`, {
        method: "DELETE",
      }).then((r) => {
        if (!r.ok) throw new Error(`API ${r.status}`);
      });
    },
    onSuccess: () => {
      toast.success("Device deleted");
      router.push(`/properties/${id}`);
    },
    onError: () => {
      toast.error("Failed to delete device");
    },
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="h-4 w-48 bg-surface-2 rounded animate-pulse mb-6" />
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-surface border border-border rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (!device) {
    return (
      <div className="p-8">
        <p className="font-body font-light text-sm text-text-3">Device not found.</p>
      </div>
    );
  }

  const isMatter = device.vendor === "matter";
  const isShelly = device.vendor === "shelly" || device.vendor === "demo";

  // Use live-resolved online status for Shelly; fall back to device.online for others
  const resolvedOnline = isShelly && liveOnline !== null ? liveOnline : device.online;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-8 max-w-7xl mx-auto"
    >
      <Link
        href={`/properties/${id}`}
        className="flex items-center gap-1.5 text-sm text-text-3 hover:text-text-2 mb-6 transition-colors"
      >
        <ArrowLeft size={14} />
        {property?.name ?? "Property"}
      </Link>

      <div className="mb-6">
        <div className="flex items-start justify-between gap-3">
          <h2 className="font-display text-2xl text-text">{device.name}</h2>
          <div className="flex items-center gap-2 mt-1 flex-shrink-0">
            <span
              className={cn(
                "inline-flex items-center font-mono text-xs px-2.5 py-0.5 rounded-full border",
                resolvedOnline
                  ? "bg-green-bg text-green border-green/20"
                  : "bg-surface-2 text-text-3 border-border"
              )}
            >
              {resolvedOnline ? "Online" : "Offline"}
            </span>

            {/* ⋯ menu */}
            <div className="relative">
              <button
                onClick={() => setMenuOpen((v) => !v)}
                className="w-8 h-8 flex items-center justify-center rounded-lg border border-border text-text-3 hover:border-border-strong hover:text-text-2 transition-colors"
              >
                <MoreHorizontal size={15} />
              </button>
              <AnimatePresence>
                {menuOpen && (
                  <>
                    <div className="fixed inset-0 z-30" onClick={() => setMenuOpen(false)} />
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95, y: -4 }}
                      animate={{ opacity: 1, scale: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.95, y: -4 }}
                      transition={{ duration: 0.1 }}
                      className="absolute right-0 top-10 z-40 w-44 bg-surface border border-border rounded-xl overflow-hidden"
                    >
                      <button
                        onClick={() => {
                          setMenuOpen(false);
                          setShowDeleteDialog(true);
                        }}
                        className="w-full flex items-center gap-2.5 px-4 py-3 text-sm font-body font-light text-red hover:bg-red-bg transition-colors"
                      >
                        <Trash2 size={13} />
                        Delete device
                      </button>
                    </motion.div>
                  </>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 mt-2 flex-wrap">
          <VendorBadge vendor={device.vendor} />
          <span className="font-body font-light text-xs text-text-3 capitalize">{device.type}</span>
          {room && (
            <>
              <span className="text-border-strong">·</span>
              <span className="font-body font-light text-xs text-text-3">{room.name}</span>
            </>
          )}
          {property && (
            <>
              <span className="text-border-strong">·</span>
              <span className="font-body font-light text-xs text-text-3">{property.name}</span>
            </>
          )}
        </div>

        {/* Link to Intelligence for AI insights */}
        <Link
          href={`/intelligence`}
          className="inline-block mt-2 font-body font-light text-xs text-text-3 hover:text-text-2 transition-colors"
        >
          View AI insights for this device →
        </Link>
      </div>

      {/* Two-column layout — 60/40 */}
      <div className="lg:grid lg:grid-cols-[3fr_2fr] lg:gap-6 space-y-4 lg:space-y-0">
        {/* Left column: readings + controls + chart */}
        <div className="space-y-4">
          {isShelly ? (
            <ShellyPanel
              deviceId={deviceId}
              deviceName={device.name}
              onOnlineResolved={setLiveOnline}
            />
          ) : isMatter ? (
            <MatterControls deviceId={deviceId} />
          ) : device.controllable ? (
            <DeviceControls device={device} />
          ) : (
            <div className="bg-surface border border-border rounded-xl p-5">
              <p className="font-body font-light text-sm text-text-3 text-center">
                Control available for Matter and locally-connected devices.
              </p>
            </div>
          )}
        </div>

        {/* Right column: state history */}
        <div>
          <DeviceStateHistory deviceId={deviceId} />
        </div>
      </div>

      {/* Delete dialog */}
      <AnimatePresence>
        {showDeleteDialog && (
          <DeleteDialog
            deviceName={device.name}
            onCancel={() => setShowDeleteDialog(false)}
            onConfirm={() => deleteMut.mutate()}
            isPending={deleteMut.isPending}
          />
        )}
      </AnimatePresence>
    </motion.div>
  );
}
