"use client"; // Client: tab switching

import { useState } from "react";
import { Plus, BookOpen, Wifi } from "lucide-react";
import { cn } from "@/lib/cn";
import { INTEGRATIONS, VENDORS } from "@/lib/fixtures";
import type { Integration, Vendor } from "@/lib/fixtures";
import { Button } from "@/components/ui/button";
import { Tag } from "@/components/ui/tag";
import { Tabs } from "@/components/ui/tabs";
import { Card, SectionHead, MonoLabel } from "@/components/ui/card";
import { DataTable } from "@/components/ui/data-table";
import type { TableColumn } from "@/components/ui/data-table";
import { PageHeader } from "@/components/ui/page-header";
import { AlertCard } from "@/components/ui/alert-card";
import { EmptyDataState } from "@/components/ui/empty-state";
import { useDemoMode } from "@/lib/use-demo-mode";
import { BluetoothPairingModal } from "@/components/integrations/bluetooth-pairing-modal";
import { useBluetoothDevices } from "@/integrations/bluetooth";

// ─── Vendor logo placeholder (graphite chip + initials) ───────────────────────

function VendorLogo({ name, size = 36 }: { name: string; size?: number }) {
  return (
    <div
      className="rounded-[10px] bg-graphite flex items-center justify-center shrink-0"
      style={{ width: size, height: size }}
    >
      <span
        className="font-serif text-white leading-none select-none"
        style={{ fontSize: Math.round(size * 0.36) }}
      >
        {name.slice(0, 2).toUpperCase()}
      </span>
    </div>
  );
}

// ─── Connected tab ────────────────────────────────────────────────────────────

function IntegrationCard({ item: i }: { item: Integration }) {
  return (
    <Card hoverable className="p-[18px]">
      <div className="flex items-center gap-3.5">
        <VendorLogo name={i.vendor} size={48} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2.5">
            <span className="font-serif text-[18px] text-text">{i.vendor}</span>
            {i.status === "ACTIVE" ? (
              <Tag variant="ok" withDot>
                active
              </Tag>
            ) : (
              <Tag variant="warn" withDot>
                token expired
              </Tag>
            )}
          </div>
          <MonoLabel className="mt-1 block">property · {i.ownerName}</MonoLabel>
        </div>
        <Button variant={i.needsReauth ? "primary" : "ghost"} size="sm">
          {i.needsReauth ? "Reauthorize" : "Manage"}
        </Button>
      </div>

      <div className="h-px bg-border my-3.5" />

      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "devices", value: String(i.devices), mono: true },
          { label: "last sync", value: i.lastSync, mono: false },
          { label: "connected", value: i.connectedAt, mono: true },
        ].map(({ label, value, mono }) => (
          <div key={label}>
            <MonoLabel>{label}</MonoLabel>
            <p
              className={cn(
                "mt-1 m-0",
                mono
                  ? "font-mono text-[18px] font-semibold text-text"
                  : "text-[13px] text-text",
              )}
            >
              {value}
            </p>
          </div>
        ))}
      </div>

      <div className="flex gap-1.5 mt-3.5 flex-wrap">
        {i.scopes.map((s) => (
          <Tag key={s} variant="neutral">
            {s}
          </Tag>
        ))}
      </div>
    </Card>
  );
}

function ConnectedTab({
  bluetoothDevices,
}: {
  bluetoothDevices: Array<{ id: string; name: string; mac_address: string }>;
}) {
  const reauth = INTEGRATIONS.find((i) => i.needsReauth);
  return (
    <>
      {reauth && (
        <AlertCard
          severity="amber"
          title="SmartThings token expired"
          desc="Your portfolio's SmartThings access token expired 6 hours ago. 12 devices are not receiving state updates. Reconnect to restore — your scopes will carry over."
          meta="Integration · Northern Portfolio · Today 03:14"
          actions={["Reauthorize", "Open integration"]}
        />
      )}
      <SectionHead
        title="Connected vendors"
        sub={`${INTEGRATIONS.length} integrations · ${bluetoothDevices.length} Bluetooth devices`}
      />
      <div className="grid grid-cols-2 gap-3">
        {INTEGRATIONS.map((i) => (
          <IntegrationCard key={i.id} item={i} />
        ))}
      </div>

      {bluetoothDevices.length > 0 && (
        <>
          <SectionHead
            title="Bluetooth devices"
            sub={`${bluetoothDevices.length} PAIRED DEVICES`}
          />
          <div className="grid grid-cols-2 gap-3">
            {bluetoothDevices.map((device) => (
              <Card key={device.id} hoverable className="p-[18px]">
                <div className="flex items-center gap-3.5">
                  <div className="w-12 h-12 rounded-[10px] bg-accent/10 flex items-center justify-center">
                    <Wifi size={20} className="text-accent" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[13px] font-medium text-text truncate">
                      {device.name}
                    </p>
                    <p className="text-[11px] font-mono text-text-3">
                      {device.mac_address}
                    </p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </>
      )}
    </>
  );
}

// ─── Catalog tab ──────────────────────────────────────────────────────────────

const CATALOG_CATS = [
  "All vendors",
  "Thermostats",
  "Lights",
  "Locks",
  "Sensors",
  "Plugs & meters",
  "Hubs & bridges",
];

function VendorCard({ v }: { v: Vendor }) {
  return (
    <Card hoverable className="p-[18px] flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <VendorLogo name={v.name} size={36} />
        <div className="flex-1">
          <p className="text-[14px] font-semibold text-text m-0">{v.name}</p>
          <p className="text-[12px] text-text-3 mt-0.5 m-0">{v.cats}</p>
        </div>
        {v.connected && (
          <Tag variant="ok" withDot>
            connected
          </Tag>
        )}
      </div>
      <div className="h-px bg-border" />
      <div className="flex justify-between items-center">
        <MonoLabel>{v.connected ? "manage" : "set up oauth"}</MonoLabel>
        <Button variant={v.connected ? "secondary" : "primary"} size="sm">
          {v.connected ? "Manage" : "Connect"}
        </Button>
      </div>
    </Card>
  );
}

function BluetoothVendorCard({ onPair }: { onPair: () => void }) {
  return (
    <Card hoverable className="p-[18px] flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-[7px] bg-accent flex items-center justify-center">
          <Wifi size={18} className="text-white" />
        </div>
        <div className="flex-1">
          <p className="text-[14px] font-semibold text-text m-0">Bluetooth</p>
          <p className="text-[12px] text-text-3 mt-0.5 m-0">
            Web Bluetooth API
          </p>
        </div>
      </div>
      <div className="h-px bg-border" />
      <div className="flex justify-between items-center">
        <MonoLabel>pair device</MonoLabel>
        <Button variant="primary" size="sm" onClick={onPair}>
          Pair
        </Button>
      </div>
    </Card>
  );
}

function CatalogTab({ onBluetoothPair }: { onBluetoothPair: () => void }) {
  const [cat, setCat] = useState("All vendors");
  return (
    <>
      <div className="flex gap-1.5 flex-wrap">
        {CATALOG_CATS.map((c) => (
          <button
            key={c}
            onClick={() => setCat(c)}
            className="border-0 p-0 bg-transparent cursor-pointer"
          >
            <Tag variant={cat === c ? "graphite" : "neutral"}>{c}</Tag>
          </button>
        ))}
      </div>
      <div className="grid grid-cols-3 gap-3">
        <BluetoothVendorCard onPair={onBluetoothPair} />
        {VENDORS.map((v) => (
          <VendorCard key={v.id} v={v} />
        ))}
      </div>
    </>
  );
}

// ─── Webhooks tab ─────────────────────────────────────────────────────────────

const WEBHOOK_ROWS = [
  {
    vendor: "Nest",
    topic: "device.state",
    events: "1,847",
    last: "2 min ago",
    status: "active",
  },
  {
    vendor: "Hue",
    topic: "lights.changed",
    events: "4,329",
    last: "30 sec ago",
    status: "active",
  },
  {
    vendor: "August",
    topic: "lock.state",
    events: "412",
    last: "1 min ago",
    status: "active",
  },
  {
    vendor: "Shelly",
    topic: "energy.usage",
    events: "8,201",
    last: "1 min ago",
    status: "active",
  },
  {
    vendor: "SmartThings",
    topic: "hub.events",
    events: "230",
    last: "6 h ago",
    status: "error",
  },
  {
    vendor: "Ecobee",
    topic: "thermostat.state",
    events: "942",
    last: "5 min ago",
    status: "active",
  },
];

type WebhookRow = (typeof WEBHOOK_ROWS)[number];

const WEBHOOK_COLS: TableColumn<WebhookRow>[] = [
  {
    k: "vendor",
    label: "Vendor",
    w: "1fr",
    render: (r) => <span className="font-medium">{r.vendor}</span>,
  },
  {
    k: "topic",
    label: "Topic",
    w: "1.4fr",
    render: (r) => (
      <span className="font-mono text-[12px] text-text-2">{r.topic}</span>
    ),
  },
  {
    k: "events",
    label: "Events · 24h",
    w: "1fr",
    align: "right",
    render: (r) => (
      <span className="[font-variant-numeric:tabular-nums]">{r.events}</span>
    ),
  },
  {
    k: "last",
    label: "Last received",
    w: "1fr",
    render: (r) => <MonoLabel>{r.last}</MonoLabel>,
  },
  {
    k: "status",
    label: "Status",
    w: "0.8fr",
    render: (r) => (
      <Tag variant={r.status === "active" ? "ok" : "alert"} withDot>
        {r.status}
      </Tag>
    ),
  },
  {
    k: "act",
    label: "",
    w: "70px",
    align: "right",
    render: () => (
      <Button variant="ghost" size="sm">
        Rotate
      </Button>
    ),
  },
];

function WebhooksTab() {
  return (
    <>
      <SectionHead
        title="Webhook subscriptions"
        sub="VENDOR → ALPHACON · INCOMING EVENTS"
      />
      <DataTable columns={WEBHOOK_COLS} rows={WEBHOOK_ROWS} />
    </>
  );
}

// ─── Errors tab ───────────────────────────────────────────────────────────────

const ERROR_ROWS = [
  {
    time: "today 03:14",
    vendor: "SmartThings",
    code: "AuthExpired",
    message: "Refresh token returned 401 invalid_grant",
    retriable: true,
    userVisible: true,
  },
  {
    time: "Y'day 18:32",
    vendor: "Nest",
    code: "RateLimited",
    message: "Backoff for 47s · /thermostat/cmd",
    retriable: true,
    userVisible: false,
  },
  {
    time: "Y'day 11:09",
    vendor: "Hue",
    code: "DeviceOffline",
    message: "Bridge unreachable for 3 min · Maple Court",
    retriable: false,
    userVisible: true,
  },
  {
    time: "29 Mar",
    vendor: "August",
    code: "CommandRejected",
    message: "Lock not in manual mode · Larkspur House",
    retriable: false,
    userVisible: true,
  },
];

type ErrorRow = (typeof ERROR_ROWS)[number];

const ERROR_COLS: TableColumn<ErrorRow>[] = [
  {
    k: "time",
    label: "Time",
    w: "120px",
    render: (r) => <MonoLabel>{r.time}</MonoLabel>,
  },
  { k: "vendor", label: "Vendor", w: "1fr" },
  {
    k: "code",
    label: "Error",
    w: "1fr",
    render: (r) => (
      <span className="font-mono text-[12px] font-medium text-red">
        {r.code}
      </span>
    ),
  },
  {
    k: "message",
    label: "Message",
    w: "2.5fr",
    wrap: true,
    render: (r) => <span className="text-[12px] text-text-2">{r.message}</span>,
  },
  {
    k: "flags",
    label: "Flags",
    w: "1.2fr",
    render: (r) => (
      <div className="flex gap-1">
        {r.retriable && <Tag variant="neutral">retriable</Tag>}
        {r.userVisible && <Tag variant="warn">user-visible</Tag>}
      </div>
    ),
  },
];

function ErrorsTab() {
  return (
    <>
      <SectionHead
        title="Adapter errors"
        sub="LAST 7 DAYS · CLASSIFIED BY ADAPTERROR HIERARCHY"
      />
      <DataTable columns={ERROR_COLS} rows={ERROR_ROWS} />
    </>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

export function IntegrationsScreen() {
  const { demoMode } = useDemoMode();
  const [tab, setTab] = useState("connected");
  const [showBluetoothModal, setShowBluetoothModal] = useState(false);
  const { data: bluetoothDevices = [] } = useBluetoothDevices();

  if (!demoMode) {
    return (
      <>
        <PageHeader
          eyebrow="WORKSPACE"
          title="Integrations"
          sub="No data"
          primary={
            <Button variant="primary" icon={Plus}>
              Connect vendor
            </Button>
          }
        />
        <EmptyDataState />
      </>
    );
  }

  const active = INTEGRATIONS.filter((i) => i.status === "ACTIVE").length;

  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Integrations"
        sub={`${INTEGRATIONS.length} connections · ${active} active · 1 needs reauth`}
        primary={
          <Button variant="primary" icon={Plus}>
            Connect vendor
          </Button>
        }
        secondary={
          <Button variant="secondary" icon={BookOpen}>
            View adapter docs
          </Button>
        }
      />

      <div className="px-7 border-b border-border bg-surface">
        <Tabs
          value={tab}
          onChange={setTab}
          tabs={[
            { id: "connected", label: "Connected", count: INTEGRATIONS.length },
            { id: "catalog", label: "Catalog", count: 10 },
            { id: "webhooks", label: "Webhooks", count: 18 },
            { id: "errors", label: "Errors", count: 1 },
          ]}
        />
      </div>

      <div className="px-7 pt-5 pb-8 flex flex-col gap-5">
        {tab === "connected" && (
          <ConnectedTab bluetoothDevices={bluetoothDevices} />
        )}
        {tab === "catalog" && (
          <CatalogTab onBluetoothPair={() => setShowBluetoothModal(true)} />
        )}
        {tab === "webhooks" && <WebhooksTab />}
        {tab === "errors" && <ErrorsTab />}
      </div>

      {showBluetoothModal && (
        <BluetoothPairingModal
          propertyId="550e8400-e29b-41d4-a716-446655440000"
          onSuccess={() => setShowBluetoothModal(false)}
          onCancel={() => setShowBluetoothModal(false)}
        />
      )}
    </>
  );
}
