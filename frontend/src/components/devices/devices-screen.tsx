"use client"; // Client: device filter, drawer open/close state

import { useState } from "react";
import {
  X,
  Plus,
  RefreshCw,
  ChevronRight,
  Thermometer,
  Lightbulb,
  Lock,
  Plug,
  Radio,
  Droplets,
  Zap,
  Monitor,
  Sparkles,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { DEVICES_MAPLE } from "@/lib/fixtures";
import type { Device, DeviceCategory } from "@/lib/fixtures";
import { useDemoMode } from "@/lib/use-demo-mode";
import { Button } from "@/components/ui/button";
import { Tag } from "@/components/ui/tag";
import { Card, SectionHead, MonoLabel } from "@/components/ui/card";
import { StatCard } from "@/components/ui/stat-card";
import { DataTable } from "@/components/ui/data-table";
import type { TableColumn } from "@/components/ui/data-table";
import { PageHeader } from "@/components/ui/page-header";

// ─── Icon mapping ─────────────────────────────────────────────────────────────

const CATEGORY_ICON: Record<DeviceCategory, LucideIcon> = {
  THERMOSTAT: Thermometer,
  LIGHT: Lightbulb,
  LOCK: Lock,
  PLUG: Plug,
  SENSOR_MOTION: Radio,
  SENSOR_LEAK: Droplets,
  SENSOR_CONTACT: Radio,
  ENERGY_METER: Zap,
  SWITCH: Plug,
  HUB: Monitor,
};

function categoryIcon(cat: DeviceCategory): LucideIcon {
  return CATEGORY_ICON[cat] ?? Monitor;
}

// ─── Activity generation (fixture data per device category) ───────────────────

type ActivityTone = "ok" | "warn" | "alert" | "neutral";
type ActivityKind = "AGENT" | "AUTOMATION" | "USER" | "SYSTEM" | "VENDOR";

interface ActivityEvent {
  time: string;
  kind: ActivityKind;
  who: string;
  text: string;
  tone: ActivityTone;
}

// Static activity templates per category — vendor/state slots filled at call time
const CATEGORY_ACTIVITY: Partial<Record<DeviceCategory, ActivityEvent[]>> = {
  THERMOSTAT: [
    {
      time: "today 11:24",
      kind: "AGENT",
      who: "Agent",
      text: "Set point lowered to 14°C — vacancy cool-down",
      tone: "ok",
    },
    {
      time: "today 08:42",
      kind: "USER",
      who: "Marcus Chen",
      text: "Approved agent suggestion to lower heating",
      tone: "ok",
    },
    {
      time: "yesterday 18:30",
      kind: "AUTOMATION",
      who: "Pre-arrival warm-up",
      text: "Raised to 20°C ahead of expected occupancy",
      tone: "ok",
    },
    {
      time: "yesterday 06:00",
      kind: "SYSTEM",
      who: "System",
      text: "Mode changed heat → auto on schedule",
      tone: "neutral",
    },
  ],
  LIGHT: [
    {
      time: "today 07:02",
      kind: "AUTOMATION",
      who: "Morning scene",
      text: "Brightness set to 60%, warm white",
      tone: "ok",
    },
    {
      time: "yesterday 23:10",
      kind: "AUTOMATION",
      who: "Bedtime",
      text: "Turned off",
      tone: "neutral",
    },
    {
      time: "yesterday 19:44",
      kind: "USER",
      who: "Marcus Chen",
      text: "Turned on from device console",
      tone: "ok",
    },
  ],
  LOCK: [
    {
      time: "today 09:01",
      kind: "USER",
      who: "Olu Adebayo",
      text: "Unlocked remotely for a contractor visit",
      tone: "ok",
    },
    {
      time: "today 09:36",
      kind: "SYSTEM",
      who: "System",
      text: "Auto-relocked after 35 min",
      tone: "neutral",
    },
    {
      time: "yesterday 14:20",
      kind: "VENDOR",
      who: "—",
      text: "Battery level reported: 72%",
      tone: "neutral",
    },
  ],
  ENERGY_METER: [
    {
      time: "30s ago",
      kind: "VENDOR",
      who: "—",
      text: "Live reading: —",
      tone: "neutral",
    },
    {
      time: "today 07:30",
      kind: "SYSTEM",
      who: "System",
      text: "Daily energy snapshot collected",
      tone: "ok",
    },
  ],
  SENSOR_MOTION: [
    {
      time: "3m ago",
      kind: "VENDOR",
      who: "—",
      text: "Motion cleared",
      tone: "neutral",
    },
    {
      time: "yesterday 21:14",
      kind: "VENDOR",
      who: "—",
      text: "Motion detected",
      tone: "neutral",
    },
  ],
  SENSOR_LEAK: [
    {
      time: "10m ago",
      kind: "VENDOR",
      who: "—",
      text: "Reading: dry",
      tone: "ok",
    },
    {
      time: "1 Apr 03:00",
      kind: "SYSTEM",
      who: "System",
      text: "Self-test passed",
      tone: "ok",
    },
  ],
};

function deviceActivity(d: Device): ActivityEvent[] {
  const base: ActivityEvent[] = [];
  if (!d.reachable) {
    base.push({
      time: "2d ago",
      kind: "VENDOR",
      who: d.vendor,
      text: "Stopped reporting — last heartbeat received, then silence",
      tone: "alert",
    });
    base.push({
      time: "2d ago",
      kind: "SYSTEM",
      who: "System",
      text: "Marked unreachable after 3 missed polls",
      tone: "warn",
    });
  }
  if (d.alert && d.reachable) {
    base.push({
      time: "today 08:14",
      kind: "AGENT",
      who: "Agent",
      text: "Flagged: running while unit is vacant — published an insight",
      tone: "warn",
    });
  }
  const template = (
    CATEGORY_ACTIVITY[d.category] ?? [
      {
        time: "today",
        kind: "VENDOR" as ActivityKind,
        who: "—",
        text: `State: ${d.state}`,
        tone: "neutral" as ActivityTone,
      },
    ]
  ).map((e) => ({
    ...e,
    who: e.who === "—" ? d.vendor : e.who,
    text: e.text.replace("—", d.state),
  }));
  const tail: ActivityEvent[] = [
    {
      time: "20 Jan 2026",
      kind: "SYSTEM",
      who: "System",
      text: `Paired via ${d.vendor} integration · owner: property`,
      tone: "neutral",
    },
  ];
  return [...base, ...template, ...tail];
}

// ─── Device drawer ────────────────────────────────────────────────────────────

const KIND_COLOR: Record<ActivityKind, string> = {
  AGENT: "text-graphite",
  AUTOMATION: "text-text-2",
  USER: "text-text-2",
  SYSTEM: "text-text-3",
  VENDOR: "text-amber",
};

const TONE_DOT: Record<ActivityTone, string> = {
  ok: "bg-green",
  warn: "bg-amber",
  alert: "bg-red",
  neutral: "bg-text-3",
};

function MetaCell({
  label,
  value,
  mono,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="bg-bg border border-border rounded-[9px] px-3 py-2.5">
      <MonoLabel>{label}</MonoLabel>
      <p
        className={cn(
          "text-[13px] mt-1 text-text m-0",
          mono && "font-mono text-[12px]",
        )}
      >
        {value}
      </p>
    </div>
  );
}

function DeviceDrawer({
  device: d,
  onClose,
}: {
  device: Device;
  onClose: () => void;
}) {
  const DevIcon = categoryIcon(d.category);
  const events = deviceActivity(d);

  return (
    <div className="fixed inset-0 z-[60] flex justify-end">
      <div
        onClick={onClose}
        className="absolute inset-0"
        style={{ background: "rgba(16,24,40,0.28)" }}
      />
      <div className="relative w-[440px] max-w-[92vw] h-full bg-surface border-l border-border shadow-lg flex flex-col">
        {/* Header */}
        <div className="px-5 py-[18px] border-b border-border flex items-start gap-3">
          <div className="w-[38px] h-[38px] rounded-[8px] bg-surface-2 flex items-center justify-center shrink-0">
            <DevIcon size={18} strokeWidth={1.5} className="text-text-2" />
          </div>
          <div className="flex-1 min-w-0">
            <p
              className={cn(
                "font-serif text-[19px] leading-[1.2] m-0",
                d.alert ? "text-amber" : "text-text",
              )}
            >
              {d.name}
            </p>
            <MonoLabel className="mt-[3px] block">
              {d.category.replace(/_/g, " ").toLowerCase()} · {d.room}
            </MonoLabel>
          </div>
          <button
            onClick={onClose}
            aria-label="Close device drawer"
            className="text-text-3 hover:text-text p-1"
          >
            <X size={18} strokeWidth={1.5} />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-5 py-[18px] flex flex-col gap-5">
          {/* Live state */}
          <div className="bg-bg border border-border rounded-card p-4">
            <div className="flex justify-between items-center">
              <MonoLabel>current state</MonoLabel>
              <Tag
                variant={d.reachable ? (d.alert ? "warn" : "ok") : "alert"}
                withDot
              >
                {d.reachable ? "online" : "unreachable"}
              </Tag>
            </div>
            <p
              className={cn(
                "font-serif text-[24px] mt-2 m-0",
                d.alert ? "text-amber" : "text-text",
              )}
            >
              {d.reachable ? d.state : "No signal"}
            </p>
            <MonoLabel className="mt-1.5 block">
              last seen · {d.lastSeen}
            </MonoLabel>
          </div>

          {/* Meta grid */}
          <div className="grid grid-cols-2 gap-3">
            <MetaCell label="Vendor" value={d.vendor} />
            <MetaCell label="Owner" value="Property" />
            <MetaCell label="Room" value={d.room} />
            <MetaCell label="Device ID" value={d.id} mono />
          </div>

          {/* Capabilities */}
          <div>
            <MonoLabel className="mb-2 block">capabilities</MonoLabel>
            <div className="flex gap-1.5 flex-wrap">
              {d.capabilities.map((c) => (
                <Tag key={c} variant="neutral">
                  {c.replace(/_/g, " ").toLowerCase()}
                </Tag>
              ))}
            </div>
          </div>

          {/* Quick controls */}
          <div className="flex gap-2 flex-wrap">
            <Button variant="secondary" size="sm" icon={RefreshCw}>
              Re-sync
            </Button>
            <Button variant="secondary" size="sm" icon={Sparkles}>
              Ask agent
            </Button>
            {!d.reachable && (
              <Button variant="primary" size="sm" icon={RefreshCw}>
                Restart via hub
              </Button>
            )}
          </div>

          {/* Activity timeline */}
          <div>
            <h3 className="text-[13px] font-semibold text-text m-0 mb-3">
              Activity
            </h3>
            <ul className="list-none m-0 p-0">
              {events.map((e, i) => (
                <li key={i} className="flex gap-3 pb-4 last:pb-0">
                  <div className="flex flex-col items-center shrink-0">
                    <span
                      className={cn(
                        "w-[9px] h-[9px] rounded-full mt-1 shrink-0",
                        TONE_DOT[e.tone],
                      )}
                    />
                    {i < events.length - 1 && (
                      <span className="w-px flex-1 bg-border mt-1" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0 pb-px">
                    <p className="text-[13px] text-text leading-[1.45] m-0">
                      {e.text}
                    </p>
                    <div className="flex items-center gap-1.5 mt-1">
                      <MonoLabel className={KIND_COLOR[e.kind]}>
                        {e.kind.toLowerCase()}
                      </MonoLabel>
                      <span className="text-text-3 text-[11px]">
                        · {e.who} ·
                      </span>
                      <MonoLabel>{e.time}</MonoLabel>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Device list with filter chips ───────────────────────────────────────────

type DeviceFilter = "all" | "alert" | "offline";

const DEVICE_COLUMNS: TableColumn<Device>[] = [
  {
    k: "name",
    label: "Device",
    w: "1.5fr",
    render: (r) => {
      const Icon = categoryIcon(r.category);
      return (
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-[7px] bg-surface-2 flex items-center justify-center shrink-0">
            <Icon size={14} strokeWidth={1.5} className="text-text-2" />
          </div>
          <div className="min-w-0">
            <p
              className={cn(
                "text-[13px] font-medium m-0",
                r.alert ? "text-amber" : "text-text",
              )}
            >
              {r.name}
            </p>
            <MonoLabel className="mt-0.5 block">
              {r.category.replace(/_/g, " ").toLowerCase()}
            </MonoLabel>
          </div>
        </div>
      );
    },
  },
  {
    k: "room",
    label: "Room",
    w: "1.2fr",
    render: (r) => <span className="text-[12px] text-text-2">{r.room}</span>,
  },
  {
    k: "vendor",
    label: "Vendor",
    w: "0.8fr",
    render: (r) => <span className="text-[12px] text-text-2">{r.vendor}</span>,
  },
  {
    k: "state",
    label: "State",
    w: "1fr",
    render: (r) => (
      <span
        className={cn(
          "text-[13px]",
          r.reachable
            ? r.alert
              ? "text-amber font-medium"
              : "text-text"
            : "text-text-3",
        )}
      >
        {r.reachable ? r.state : "Unreachable"}
      </span>
    ),
  },
  {
    k: "lastSeen",
    label: "Last seen",
    w: "0.8fr",
    render: (r) => (
      <MonoLabel className={r.reachable ? "" : "text-amber"}>
        {r.lastSeen}
      </MonoLabel>
    ),
  },
  {
    k: "act",
    label: "",
    w: "30px",
    align: "right",
    render: () => (
      <ChevronRight size={14} strokeWidth={1.5} className="text-text-3" />
    ),
  },
];

function DeviceList({
  devices,
  onSelect,
}: {
  devices: Device[];
  onSelect: (d: Device) => void;
}) {
  const [filter, setFilter] = useState<DeviceFilter>("all");

  const filtered =
    filter === "offline"
      ? devices.filter((d) => !d.reachable)
      : filter === "alert"
        ? devices.filter((d) => d.alert)
        : devices;

  const CHIPS: { id: DeviceFilter; label: string; count: number }[] = [
    { id: "all", label: "All", count: devices.length },
    {
      id: "alert",
      label: "Needs attention",
      count: devices.filter((d) => d.alert).length,
    },
    {
      id: "offline",
      label: "Unreachable",
      count: devices.filter((d) => !d.reachable).length,
    },
  ];

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-1.5 flex-wrap">
        {CHIPS.map(({ id, label, count }) => (
          <button
            key={id}
            onClick={() => setFilter(id)}
            className={cn(
              "inline-flex items-center gap-2 rounded-[9px] px-3 py-1.5 text-[12px] font-medium",
              "border cursor-pointer font-sans transition-colors duration-[120ms]",
              filter === id
                ? "bg-graphite text-white border-graphite"
                : "bg-surface text-text-2 border-border hover:border-border-strong",
            )}
          >
            {label}
            <span className="font-mono text-[10px] opacity-80">{count}</span>
          </button>
        ))}
        <div className="flex-1" />
        <Button variant="secondary" size="sm" icon={RefreshCw}>
          Re-sync from vendors
        </Button>
      </div>
      <DataTable
        columns={DEVICE_COLUMNS}
        rows={filtered}
        onRowClick={onSelect}
      />
    </div>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

export function DevicesScreen() {
  const [selected, setSelected] = useState<Device | null>(null);
  const { demoMode, toggleDemoMode } = useDemoMode();
  const total = DEVICES_MAPLE.length;
  const online = DEVICES_MAPLE.filter((d) => d.reachable).length;
  const unreachable = DEVICES_MAPLE.filter((d) => !d.reachable).length;

  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Devices"
        sub="401 devices across 12 properties · synced from connected vendor integrations"
        primary={
          <Button variant="primary" icon={Plus}>
            Pair device
          </Button>
        }
        secondary={
          <div className="flex gap-2">
            <Button
              variant={demoMode ? "primary" : "secondary"}
              size="sm"
              onClick={() => toggleDemoMode()}
            >
              {demoMode ? "Demo Mode ON" : "Demo Mode OFF"}
            </Button>
            <Button variant="secondary" icon={RefreshCw}>
              Re-sync
            </Button>
          </div>
        }
      />

      <div className="px-7 pt-5 pb-8 flex flex-col gap-5">
        <div className="grid grid-cols-4 gap-3">
          <StatCard
            label="Total devices"
            value="401"
            sub="Across 12 properties"
          />
          <StatCard label="Online" value={online} sub="Reporting normally" />
          <StatCard
            label="Categories"
            value={8}
            sub="Thermostats, lights, locks, sensors…"
          />
          <StatCard
            label="Unreachable"
            value={unreachable}
            variant="amber"
            sub={
              <span className="text-amber">Hallway motion · Maple Court</span>
            }
          />
        </div>

        <div>
          <SectionHead
            title="All devices"
            sub={`MAPLE COURT — SHOWING ${total} OF 401 · FILTER BY PROPERTY ABOVE`}
            right={
              <Button variant="ghost" size="sm">
                Filters
              </Button>
            }
          />
          <DeviceList devices={DEVICES_MAPLE} onSelect={setSelected} />
        </div>

        <Card className="p-[18px] flex items-start gap-3.5">
          <div className="w-9 h-9 rounded-[8px] bg-graphite flex items-center justify-center shrink-0">
            <RefreshCw size={16} strokeWidth={1.5} color="#ffffff" />
          </div>
          <div className="flex-1">
            <p className="text-[13px] font-semibold text-text m-0">
              Devices stay in sync with your vendors
            </p>
            <p className="text-[12px] text-text-2 mt-1 leading-[1.6] m-0 max-w-[720px]">
              Every device is discovered through a connected integration and
              owned by the property. State updates arrive over vendor webhooks;
              if a device looks stale, re-sync pulls the latest from the vendor
              cloud.
            </p>
            <div className="flex gap-2 mt-3">
              <Button variant="tagSec" size="sm">
                Manage integrations
              </Button>
              <Button variant="tagSec" size="sm">
                View sync log
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {selected && (
        <DeviceDrawer device={selected} onClose={() => setSelected(null)} />
      )}
    </>
  );
}
