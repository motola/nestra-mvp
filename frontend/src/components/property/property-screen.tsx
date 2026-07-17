"use client"; // Client: tab switching, devices filter state

import { useState } from "react";
import {
  Sparkles,
  Settings,
  Lock,
  Thermometer,
  Lightbulb,
  Plug,
  Radio,
  Droplets,
  Zap,
  Monitor,
  ChevronRight,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { PORTFOLIOS, ROOMS_MAPLE, AUDIT } from "@/lib/fixtures";
import { useDevices } from "@/lib/use-devices";
import { useDemoMode } from "@/lib/use-demo-mode";
import type {
  Property,
  DeviceCategory,
  Device,
  AuditEntry,
} from "@/lib/fixtures";
import { Button } from "@/components/ui/button";
import { Tag } from "@/components/ui/tag";
import { Tabs } from "@/components/ui/tabs";
import { Card, SectionHead, MonoLabel } from "@/components/ui/card";
import { StatCard } from "@/components/ui/stat-card";
import { DataTable } from "@/components/ui/data-table";
import type { TableColumn } from "@/components/ui/data-table";
import { PageHeader } from "@/components/ui/page-header";

// ─── Device icon map ──────────────────────────────────────────────────────────

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

function devIcon(cat: DeviceCategory): LucideIcon {
  return CATEGORY_ICON[cat] ?? Monitor;
}

// ─── Overview tab ─────────────────────────────────────────────────────────────

interface LiveDevice {
  name: string;
  state: string;
  icon: LucideIcon;
  since: string;
  warn: boolean;
}

const LIVE_SNAPSHOT: LiveDevice[] = [
  {
    name: "Front lock",
    state: "Locked",
    icon: Lock,
    since: "1h ago",
    warn: false,
  },
  {
    name: "Communal heating",
    state: "16°C · setback",
    icon: Thermometer,
    since: "now",
    warn: false,
  },
  {
    name: "Hallway motion",
    state: "Unreachable",
    icon: Radio,
    since: "2d ago",
    warn: true,
  },
  {
    name: "Energy meter",
    state: "1.2 kW",
    icon: Zap,
    since: "30s ago",
    warn: false,
  },
  {
    name: "Leak — under sink",
    state: "Dry",
    icon: Droplets,
    since: "10m ago",
    warn: false,
  },
  {
    name: "Communal lights",
    state: "Off",
    icon: Lightbulb,
    since: "now",
    warn: false,
  },
];

function OverviewTab({ property }: { property: Property }) {
  const { devices } = useDevices("b4e3df93-f5e0-4e8f-beaa-33e2aead82ba");
  const online = devices.filter((d) => d.reachable).length;
  const unreachable = devices.filter((d) => !d.reachable).length;
  const vacant = property.units - property.occupied;

  return (
    <>
      <div className="grid grid-cols-4 gap-3">
        <StatCard
          label="Occupancy"
          value={`${property.occupied}/${property.units}`}
          sub={`${vacant} unit${vacant !== 1 ? "s" : ""} vacant`}
        />
        <StatCard
          label="Devices online"
          value={online}
          unit={`/${devices.length}`}
          sub={
            unreachable > 0 ? (
              <span className="text-amber">
                {unreachable} sensor unreachable
              </span>
            ) : (
              "All reporting normally"
            )
          }
        />
        <StatCard
          label="Energy · today"
          value="42"
          unit="kWh"
          sub="Avg. £4.20 · on track"
        />
        <StatCard
          label="Active alerts"
          value={property.alerts}
          variant={property.alerts > 0 ? "amber" : "default"}
          sub={
            property.alerts > 0 ? (
              <span className="text-amber">Vacant heating waste</span>
            ) : (
              "No active alerts"
            )
          }
        />
      </div>

      <SectionHead
        title="Live device state"
        sub="POLLED EVERY 30S"
        right={
          <Tag variant="ok" withDot>
            Reporting
          </Tag>
        }
      />

      <div className="grid grid-cols-3 gap-3">
        {LIVE_SNAPSHOT.map((d) => {
          const Icon = d.icon;
          return (
            <Card key={d.name} className="p-4 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-[7px] bg-surface-2 flex items-center justify-center shrink-0">
                    <Icon size={14} strokeWidth={1.5} className="text-text-2" />
                  </div>
                  <span className="text-[13px] font-medium text-text">
                    {d.name}
                  </span>
                </div>
                <Tag variant={d.warn ? "warn" : "ok"} withDot>
                  {d.warn ? "Attention" : "Online"}
                </Tag>
              </div>
              <p
                className={cn(
                  "font-serif text-[18px] leading-[1.2] m-0",
                  d.warn ? "text-amber" : "text-text",
                )}
              >
                {d.state}
              </p>
              <MonoLabel>updated · {d.since}</MonoLabel>
            </Card>
          );
        })}
      </div>
    </>
  );
}

// ─── Rooms tab ────────────────────────────────────────────────────────────────

function RoomsTab() {
  return (
    <>
      <SectionHead
        title="Rooms & units"
        sub={`${ROOMS_MAPLE.length} ROOMS · 6 UNITS`}
        right={
          <>
            <Button variant="secondary" size="sm">
              Add room
            </Button>
            <Button variant="primary" size="sm">
              Add unit
            </Button>
          </>
        }
      />
      <div className="grid grid-cols-3 gap-3">
        {ROOMS_MAPLE.map((r) => (
          <Card key={r.id} className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="font-serif text-[17px] leading-[1.2] text-text m-0">
                  {r.name}
                </p>
                <MonoLabel className="mt-1 block">
                  {r.type.toLowerCase()}
                </MonoLabel>
              </div>
            </div>
            <div className="h-px bg-border my-3" />
            <div className="flex justify-between text-[12px] text-text-2">
              <span>{r.devices} devices</span>
              <span className="text-text-3">2 capabilities</span>
            </div>
          </Card>
        ))}
      </div>
    </>
  );
}

// ─── Devices tab ──────────────────────────────────────────────────────────────

type DeviceFilter = "all" | "alert" | "offline";

const DEVICE_COLS: TableColumn<Device>[] = [
  {
    k: "name",
    label: "Device",
    w: "1.5fr",
    render: (r) => {
      const Icon = devIcon(r.category);
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
    w: "0.7fr",
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

function DevicesTab() {
  const [filter, setFilter] = useState<DeviceFilter>("all");
  const { devices, loading, error } = useDevices(
    "b4e3df93-f5e0-4e8f-beaa-33e2aead82ba",
  );

  const filtered =
    filter === "offline"
      ? devices.filter((d) => !d.reachable)
      : filter === "alert"
        ? devices.filter((d) => d.alert)
        : devices;

  const chips: { id: DeviceFilter; label: string; count: number }[] = [
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

  if (loading) {
    return (
      <div className="bg-surface border border-border rounded-[13px] p-10 text-center">
        <p className="text-[13px] text-text-2">Loading devices...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-surface border border-border rounded-[13px] p-10 text-center">
        <p className="text-[13px] text-amber">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-1.5 flex-wrap">
        {chips.map(({ id, label, count }) => (
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
      </div>
      {devices.length === 0 ? (
        <div className="bg-surface border border-border rounded-[13px] p-10 text-center">
          <p className="text-[13px] text-text-2">
            No devices found. Check demo mode or configure integrations.
          </p>
        </div>
      ) : (
        <DataTable columns={DEVICE_COLS} rows={filtered} />
      )}
    </div>
  );
}

// ─── Automations tab ──────────────────────────────────────────────────────────

function AutomationsTab() {
  return (
    <div className="bg-surface border border-border rounded-[13px] p-10 text-center">
      <p className="font-serif text-[22px] text-text m-0">
        4 automations active for this property
      </p>
      <p className="text-[13px] text-text-2 mt-2 max-w-[480px] mx-auto leading-[1.6] m-0">
        Open Automations to view, edit or pause. Pre-arrival warm-up, vacant
        cool-down, leak shut-off, and daily energy summary are running for this
        property.
      </p>
      <div className="mt-4">
        <Button variant="primary">Open automations</Button>
      </div>
    </div>
  );
}

// ─── Energy tab ───────────────────────────────────────────────────────────────

const ENERGY_DAYS = ["M", "T", "W", "T", "F", "S", "S"];
const ENERGY_VALUES = [42, 39, 51, 47, 44, 38, 33];
const ENERGY_MAX = Math.max(...ENERGY_VALUES);

function EnergyTab() {
  return (
    <>
      <div className="grid grid-cols-4 gap-3">
        <StatCard
          label="This week"
          value="294"
          unit="kWh"
          sub={<span className="text-green">↓ 8% vs last week</span>}
        />
        <StatCard
          label="This month"
          value="1,247"
          unit="kWh"
          sub="£124 estimated"
        />
        <StatCard
          label="Per occupied unit"
          value="73"
          unit="kWh"
          sub="Vs 89 kWh portfolio avg"
        />
        <StatCard label="Carbon · month" value="312" unit="kg" sub="CO₂e" />
      </div>

      <Card className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-[14px] font-semibold text-text m-0">
              Daily consumption · last 7 days
            </h3>
            <MonoLabel className="mt-1 block">
              kWh · this property only
            </MonoLabel>
          </div>
          <div className="flex gap-2">
            <Tag variant="neutral" withDot>
              Heating
            </Tag>
            <Tag variant="neutral">Lighting</Tag>
            <Tag variant="neutral">Plugs</Tag>
          </div>
        </div>
        <div className="flex items-end gap-[18px] px-2" style={{ height: 200 }}>
          {ENERGY_VALUES.map((v, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-2">
              <span className="font-mono text-[11px] text-text-3">{v}</span>
              <div
                className="w-full rounded-[6px] bg-graphite"
                style={{ height: `${(v / ENERGY_MAX) * 160}px` }}
              />
              <span className="font-mono text-[10px] text-text-3">
                {ENERGY_DAYS[i]}
              </span>
            </div>
          ))}
        </div>
      </Card>
    </>
  );
}

// ─── History tab ──────────────────────────────────────────────────────────────

const HISTORY_COLS: TableColumn<AuditEntry>[] = [
  {
    k: "time",
    label: "Time",
    w: "120px",
    render: (r) => <MonoLabel>{r.time}</MonoLabel>,
  },
  {
    k: "actor",
    label: "Actor",
    w: "150px",
    render: (r) => (
      <span className="text-[13px] font-medium text-text">{r.actor.name}</span>
    ),
  },
  {
    k: "action",
    label: "Action",
    w: "1fr",
    render: (r) => <span className="text-[12px] text-text-2">{r.action}</span>,
  },
  {
    k: "resource",
    label: "Resource",
    w: "1fr",
    render: (r) => (
      <span className="text-[12px] text-text-2">{r.resource}</span>
    ),
  },
];

function HistoryTab() {
  return (
    <>
      <SectionHead title="History" sub="AUDIT LOG · THIS PROPERTY" />
      <DataTable columns={HISTORY_COLS} rows={AUDIT} />
    </>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "rooms", label: "Rooms & units", count: ROOMS_MAPLE.length },
  { id: "devices", label: "Devices", count: DEVICES_MAPLE.length },
  { id: "automations", label: "Automations", count: 4 },
  { id: "energy", label: "Energy" },
  { id: "history", label: "History" },
];

export function PropertyScreen({ property }: { property: Property }) {
  const [tab, setTab] = useState("overview");
  const portfolio = PORTFOLIOS.find((pf) => pf.id === property.portfolio);
  const { demoMode, toggleDemoMode } = useDemoMode();

  return (
    <>
      <PageHeader
        eyebrow={
          portfolio ? `${portfolio.name.toUpperCase()} / PROPERTY` : "PROPERTY"
        }
        title={property.name}
        sub={`${property.address} · ${property.type.replace(/_/g, " ").toLowerCase()} · ${property.units} units · ${property.tz}`}
        primary={
          <Button variant="primary" icon={Sparkles}>
            Ask agent about this property
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
            <Button variant="secondary" icon={Settings}>
              Property settings
            </Button>
          </div>
        }
      />

      <div className="px-7 border-b border-border bg-surface">
        <Tabs value={tab} onChange={setTab} tabs={TABS} />
      </div>

      <div className="px-7 pt-5 pb-8 flex flex-col gap-5">
        {tab === "overview" && <OverviewTab property={property} />}
        {tab === "rooms" && <RoomsTab />}
        {tab === "devices" && <DevicesTab />}
        {tab === "automations" && <AutomationsTab />}
        {tab === "energy" && <EnergyTab />}
        {tab === "history" && <HistoryTab />}
      </div>
    </>
  );
}
