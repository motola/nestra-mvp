"use client"; // Client: tab switching

import { useState } from "react";
import { Plus, BookOpen } from "lucide-react";
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
import { VendorLogo } from "@/components/integrations/vendor-logos";
import { useProperty } from "@/lib/property/provider";

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

function ConnectedTab({ integrations }: { integrations: Integration[] }) {
  const reauth = integrations.find((i) => i.needsReauth);
  return (
    <>
      {reauth && (
        <AlertCard
          severity="amber"
          title={`${reauth.vendor} token expired`}
          desc={`Your ${reauth.vendor} access token expired. Reconnect to restore — your scopes will carry over.`}
          meta={`Integration · ${reauth.ownerName} · Today 03:14`}
          actions={["Reauthorize", "Open integration"]}
        />
      )}
      <SectionHead
        title="Connected vendors"
        sub={`${integrations.length} INTEGRATIONS`}
      />
      {integrations.length === 0 ? (
        <div className="border border-border rounded-panel p-12 text-center">
          <p className="text-[16px] text-text font-serif m-0">
            No connections yet
          </p>
          <p className="text-[14px] text-text-2 mt-2 m-0">
            Browse the Catalog to connect your first vendor and start syncing
            devices.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {integrations.map((i) => (
            <IntegrationCard key={i.id} item={i} />
          ))}
        </div>
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

function CatalogTab() {
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
        {VENDORS.map((v) => (
          <VendorCard key={v.id} v={v} />
        ))}
      </div>
    </>
  );
}

// ─── Webhooks tab ─────────────────────────────────────────────────────────────

type WebhookRow = {
  vendor: string;
  topic: string;
  events: string;
  last: string;
  status: string;
};

const WEBHOOK_ROWS: WebhookRow[] = [];

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
      {WEBHOOK_ROWS.length === 0 ? (
        <div className="border border-border rounded-panel p-12 text-center">
          <p className="text-[16px] text-text font-serif m-0">
            No webhooks configured
          </p>
          <p className="text-[14px] text-text-2 mt-2 m-0">
            When you connect vendors, their webhook subscriptions will appear
            here for monitoring.
          </p>
        </div>
      ) : (
        <DataTable columns={WEBHOOK_COLS} rows={WEBHOOK_ROWS} />
      )}
    </>
  );
}

// ─── Errors tab ───────────────────────────────────────────────────────────────

type ErrorRow = {
  time: string;
  vendor: string;
  code: string;
  message: string;
  retriable: boolean;
  userVisible: boolean;
};

const ERROR_ROWS: ErrorRow[] = [];

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
      {ERROR_ROWS.length === 0 ? (
        <div className="border border-border rounded-panel p-12 text-center">
          <p className="text-[16px] text-text font-serif m-0">No errors</p>
          <p className="text-[14px] text-text-2 mt-2 m-0">
            All integrations are running smoothly. Errors from the past 7 days
            would appear here.
          </p>
        </div>
      ) : (
        <DataTable columns={ERROR_COLS} rows={ERROR_ROWS} />
      )}
    </>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

export function IntegrationsScreen() {
  const [tab, setTab] = useState("connected");
  const { selectedProperty } = useProperty();

  // Use all integrations if no property selected (for demo), or filter by property
  const propertyIntegrations = selectedProperty
    ? INTEGRATIONS.filter((i) => i.ownerName === selectedProperty.name)
    : INTEGRATIONS;

  const active = propertyIntegrations.filter(
    (i) => i.status === "ACTIVE",
  ).length;
  const needsReauth = propertyIntegrations.filter((i) => i.needsReauth).length;

  return (
    <>
      <PageHeader
        eyebrow={selectedProperty?.name.toUpperCase() || "WORKSPACE"}
        title="Integrations"
        sub={`${propertyIntegrations.length} connections · ${active} active ${needsReauth ? `· ${needsReauth} needs reauth` : ""}`}
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
            {
              id: "connected",
              label: "Connected",
              count: propertyIntegrations.length,
            },
            { id: "catalog", label: "Catalog", count: 10 },
            { id: "webhooks", label: "Webhooks", count: 18 },
            { id: "errors", label: "Errors", count: 1 },
          ]}
        />
      </div>

      <div className="px-7 pt-5 pb-8 flex flex-col gap-5">
        {tab === "connected" && (
          <ConnectedTab integrations={propertyIntegrations} />
        )}
        {tab === "catalog" && <CatalogTab />}
        {tab === "webhooks" && <WebhooksTab />}
        {tab === "errors" && <ErrorsTab />}
      </div>
    </>
  );
}
