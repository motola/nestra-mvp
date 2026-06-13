"use client"; // Client: tab switching

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Plus,
  Download,
  Filter,
  Search,
  Sparkles,
  Zap,
  User,
  Settings,
  Plug,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { AUDIT, PORTFOLIOS } from "@/lib/fixtures";
import type { AuditEntry, AuditActorKind } from "@/lib/fixtures";
import { Button } from "@/components/ui/button";
import { Tag } from "@/components/ui/tag";
import { Tabs } from "@/components/ui/tabs";
import { Card, SectionHead, MonoLabel } from "@/components/ui/card";
import { StatCard } from "@/components/ui/stat-card";
import { DataTable } from "@/components/ui/data-table";
import type { TableColumn } from "@/components/ui/data-table";
import { PageHeader } from "@/components/ui/page-header";

// ─── Shared form primitives ───────────────────────────────────────────────────

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-[12px] font-medium text-text">{label}</label>
      {children}
      {hint && <p className="text-[11px] text-text-3 m-0">{hint}</p>}
    </div>
  );
}

function TextInput({ value }: { value: string }) {
  return (
    <input
      defaultValue={value}
      className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent"
    />
  );
}

function SelectInput({ value, options }: { value: string; options: string[] }) {
  return (
    <select
      defaultValue={value}
      className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent appearance-none"
    >
      {options.map((o) => (
        <option key={o}>{o}</option>
      ))}
    </select>
  );
}

// ─── Reusable settings card ───────────────────────────────────────────────────

function SettingsCard({
  title,
  sub,
  children,
  footer,
}: {
  title: string;
  sub?: string;
  children?: React.ReactNode;
  footer?: React.ReactNode;
}) {
  return (
    <Card className="p-5 flex flex-col gap-4">
      <div>
        <h3 className="text-[14px] font-semibold text-text m-0">{title}</h3>
        {sub && (
          <p className="text-[12px] text-text-3 mt-1 leading-[1.55] m-0">
            {sub}
          </p>
        )}
      </div>
      {children}
      {footer && (
        <div className="flex justify-end border-t border-border pt-3.5 mt-1">
          {footer}
        </div>
      )}
    </Card>
  );
}

// ─── Organization tab ─────────────────────────────────────────────────────────

function OrgTab() {
  return (
    <>
      <SettingsCard
        title="Organization profile"
        sub="Visible to teammates. Tenants see only the display name."
        footer={
          <Button variant="primary" size="sm">
            Save changes
          </Button>
        }
      >
        <div className="grid grid-cols-2 gap-3.5">
          <Field label="Display name">
            <TextInput value="Chen Property Holdings" />
          </Field>
          <Field label="Legal name">
            <TextInput value="Chen Holdings Ltd" />
          </Field>
          <Field label="URL slug" hint="alphacon.ai/o/chen-holdings">
            <TextInput value="chen-holdings" />
          </Field>
          <Field label="Default timezone">
            <SelectInput
              value="Europe/London"
              options={["Europe/London", "Europe/Paris", "UTC"]}
            />
          </Field>
        </div>
      </SettingsCard>

      <SettingsCard
        title="Defaults"
        sub="Applied when creating new properties or stays."
      >
        <div className="grid grid-cols-2 gap-3.5">
          <Field label="Default property type">
            <SelectInput
              value="Mixed-use"
              options={["Short-term", "Long-term", "Mixed-use", "Commercial"]}
            />
          </Field>
          <Field label="Default currency">
            <SelectInput value="GBP" options={["GBP", "EUR", "USD"]} />
          </Field>
          <Field label="Energy provider">
            <TextInput value="Octopus Energy" />
          </Field>
          <Field label="Per-kWh rate" hint="Used for estimates only">
            <TextInput value="0.247" />
          </Field>
        </div>
      </SettingsCard>

      <SettingsCard
        title="Danger zone"
        sub="Permanently delete this organization and all data."
        footer={
          <Button variant="destructive" size="sm">
            Delete organization
          </Button>
        }
      />
    </>
  );
}

// ─── Portfolios tab ───────────────────────────────────────────────────────────

const PORTFOLIO_ROWS = [
  {
    name: "Northern Portfolio",
    properties: 9,
    members: 4,
    region: "North England + Scotland",
    default: true,
  },
  {
    name: "Southern Portfolio",
    properties: 3,
    members: 2,
    region: "London + South West",
    default: false,
  },
];
type PortfolioRow = (typeof PORTFOLIO_ROWS)[number];
const PORTFOLIO_COLS: TableColumn<PortfolioRow>[] = [
  {
    k: "name",
    label: "Portfolio",
    w: "1.4fr",
    render: (r) => (
      <div className="flex items-center gap-2">
        <span className="font-serif text-[16px] text-text">{r.name}</span>
        {r.default && <Tag variant="neutral">default</Tag>}
      </div>
    ),
  },
  {
    k: "region",
    label: "Region",
    w: "1.4fr",
    render: (r) => <span className="text-[12px] text-text-2">{r.region}</span>,
  },
  {
    k: "properties",
    label: "Properties",
    w: "0.8fr",
    align: "right",
    render: (r) => (
      <span className="[font-variant-numeric:tabular-nums]">
        {r.properties}
      </span>
    ),
  },
  {
    k: "members",
    label: "Members",
    w: "0.8fr",
    align: "right",
    render: (r) => (
      <span className="[font-variant-numeric:tabular-nums]">{r.members}</span>
    ),
  },
  {
    k: "act",
    label: "",
    w: "100px",
    align: "right",
    render: () => (
      <Button variant="ghost" size="sm">
        Manage
      </Button>
    ),
  },
];

function PortfoliosTab() {
  return (
    <>
      <SectionHead
        title="Portfolios"
        sub="LEVEL 2 · GROUPS PROPERTIES UNDER A REGIONAL TEAM"
        right={
          <Button variant="primary" size="sm" icon={Plus}>
            New portfolio
          </Button>
        }
      />
      <DataTable columns={PORTFOLIO_COLS} rows={PORTFOLIO_ROWS} />
    </>
  );
}

// ─── Billing tab ──────────────────────────────────────────────────────────────

function BillingTab() {
  return (
    <>
      <Card className="p-[22px] grid grid-cols-2 gap-5">
        <div>
          <MonoLabel>Current plan</MonoLabel>
          <p className="font-serif text-[28px] text-text mt-1.5 m-0">Growth</p>
          <p className="text-[13px] text-text-2 mt-1 m-0">
            £89 per portfolio · monthly · {PORTFOLIOS.length} portfolios billed
          </p>
          <div className="flex gap-2 mt-4">
            <Button variant="primary" size="sm">
              Upgrade to Scale
            </Button>
            <Button variant="ghost" size="sm">
              View invoices
            </Button>
          </div>
        </div>
        <div>
          <MonoLabel>April 2026 · projected</MonoLabel>
          <p className="font-serif text-[28px] text-text mt-1.5 m-0 [font-variant-numeric:tabular-nums]">
            £178.00
          </p>
          <p className="text-[13px] text-text-3 mt-1 m-0">
            billed 1 May · ending 4242
          </p>
          <div className="flex gap-3 mt-4 text-[12px] text-text-2">
            <span>2 portfolios</span>
            <span>·</span>
            <span>12 properties</span>
            <span>·</span>
            <span>14 seats</span>
          </div>
        </div>
      </Card>

      <SettingsCard
        title="Agent usage"
        sub="Pay-as-you-go on top of subscription · billed monthly."
      >
        <div className="grid grid-cols-4 gap-3">
          <StatCard
            label="Conversations · April"
            value="312"
            sub="Across 4 personas"
          />
          <StatCard label="Input tokens" value="1.42M" sub="92% cached" />
          <StatCard label="Output tokens" value="318K" sub="" />
          <StatCard
            label="Cost · April"
            value="£24.12"
            sub="£12.40 last month"
          />
        </div>
      </SettingsCard>
    </>
  );
}

// ─── Security tab ─────────────────────────────────────────────────────────────

const AUTH_METHODS = [
  { l: "Email + password", on: true, hint: "Min 12 chars · zxcvbn ≥ 3" },
  { l: "Magic link", on: true, hint: "15-minute single-use links" },
  { l: "Google SSO", on: true, hint: "*.chen.holdings only" },
  { l: "Apple SSO", on: false, hint: "Not enabled" },
  { l: "Hardware key (FIDO2)", on: false, hint: "Coming soon" },
];

const SESSIONS = [
  {
    device: "MacBook · Chrome",
    where: "Leeds · 78.43.x.x",
    when: "now",
    current: true,
  },
  { device: "iPhone · Alphacon app", where: "Leeds · LTE", when: "5h ago" },
  { device: "iPad · Safari", where: "Manchester", when: "3d ago" },
];

function SecurityTab() {
  return (
    <>
      <SettingsCard
        title="Authentication"
        sub="Choose what your team can use to sign in."
      >
        {AUTH_METHODS.map((r) => (
          <div
            key={r.l}
            className="flex justify-between items-center py-2.5 border-b border-border last:border-0"
          >
            <div>
              <p className="text-[13px] font-medium text-text m-0">{r.l}</p>
              <p className="text-[11px] text-text-3 mt-0.5 m-0">{r.hint}</p>
            </div>
            <Tag variant={r.on ? "ok" : "neutral"} withDot>
              {r.on ? "on" : "off"}
            </Tag>
          </div>
        ))}
      </SettingsCard>

      <SettingsCard
        title="Sessions"
        sub="Active sessions across browsers + the Alphacon mobile app."
      >
        <div className="grid grid-cols-2 gap-3">
          {SESSIONS.map((s) => (
            <div
              key={s.device}
              className="p-3 border border-border rounded-[9px] bg-bg"
            >
              <div className="flex justify-between items-center">
                <span className="text-[13px] font-medium text-text">
                  {s.device}
                </span>
                {s.current && <Tag variant="ok">current</Tag>}
              </div>
              <p className="text-[11px] text-text-3 mt-1 m-0">
                {s.where} · {s.when}
              </p>
            </div>
          ))}
        </div>
      </SettingsCard>
    </>
  );
}

// ─── Audit log tab ────────────────────────────────────────────────────────────

const ACTOR_BG: Record<AuditActorKind, string> = {
  AGENT: "bg-graphite text-white",
  AUTOMATION: "bg-surface-2 text-text-2",
  USER: "bg-surface-2 text-text-2",
  SYSTEM: "bg-surface-2 text-text-2",
  VENDOR: "bg-amber-bg text-amber",
};

const ACTOR_ICON: Record<
  AuditActorKind,
  React.FC<{ size: number; strokeWidth: number }>
> = {
  AGENT: Sparkles,
  AUTOMATION: Zap,
  USER: User,
  SYSTEM: Settings,
  VENDOR: Plug,
};

const ACTOR_FILTER_CHIPS = [
  { label: "All actors", active: true },
  { label: "Team" },
  { label: "Agent" },
  { label: "Automations" },
  { label: "System" },
  { label: "Vendor webhooks" },
];

const RESOURCE_ROUTE: [RegExp, string][] = [
  [/^Device/, "/devices"],
  [/^Integration/, "/integrations"],
  [/^Automation|cool-down|protection|warm-up|summary/i, "/automations"],
  [/^User|Property Manager/, "/team"],
  [/^Insight|report/i, "/intelligence"],
];

function resourceRoute(resource: string): string | null {
  for (const [re, route] of RESOURCE_ROUTE) {
    if (re.test(resource)) return route;
  }
  return null;
}

const RECENT_ACTIVITY = [
  {
    time: "08:42",
    who: "Agent",
    what: "Turned off heating in Maple Court Flat 3B",
    kind: "ok",
  },
  {
    time: "08:14",
    who: "Agent",
    what: "Detected vacant heating in Maple Court Flat 3B",
    kind: "warn",
  },
  {
    time: "07:30",
    who: "Marcus",
    what: "Approved March report for team email",
    kind: "neutral",
  },
  {
    time: "06:47",
    who: "System",
    what: "Northbrook Mill hub stopped responding",
    kind: "alert",
  },
  {
    time: "Y'day",
    who: "Agent",
    what: "Drafted check-in message for Larkspur House Flat 1",
    kind: "warn",
  },
];

const DOT: Record<string, string> = {
  ok: "bg-green",
  warn: "bg-amber",
  alert: "bg-red",
  neutral: "bg-text-3",
};

function AuditTab() {
  const router = useRouter();

  const auditCols: TableColumn<AuditEntry>[] = [
    {
      k: "time",
      label: "Time",
      w: "140px",
      render: (r) => <MonoLabel>{r.time}</MonoLabel>,
    },
    {
      k: "actor",
      label: "Actor",
      w: "160px",
      render: (r) => {
        const Icon = ACTOR_ICON[r.actor.kind];
        return (
          <div className="flex items-center gap-2">
            <div
              className={cn(
                "w-[18px] h-[18px] rounded-[4px] shrink-0 flex items-center justify-center",
                ACTOR_BG[r.actor.kind],
              )}
            >
              <Icon size={11} strokeWidth={1.5} />
            </div>
            <span className="text-[12px] font-medium text-text">
              {r.actor.name}
            </span>
          </div>
        );
      },
    },
    {
      k: "action",
      label: "Action",
      w: "1fr",
      render: (r) => (
        <span className="font-mono text-[12px] text-text">{r.action}</span>
      ),
    },
    {
      k: "resource",
      label: "Resource",
      w: "1.6fr",
      render: (r) => {
        const route = resourceRoute(r.resource);
        if (!route)
          return <span className="text-[12px] text-text-2">{r.resource}</span>;
        return (
          <button
            onClick={() => router.push(route)}
            className="inline-flex items-center gap-1.5 max-w-full bg-bg border border-border rounded-[7px] px-2 py-1 cursor-pointer text-left hover:border-border-strong transition-colors duration-[120ms]"
          >
            <ChevronRight
              size={12}
              strokeWidth={1.5}
              className="text-text-3 shrink-0"
            />
            <span className="text-[12px] text-text truncate">{r.resource}</span>
          </button>
        );
      },
    },
    {
      k: "meta",
      label: "Meta · owner snapshot",
      w: "1.9fr",
      wrap: true,
      render: (r) => (
        <span className="text-[11px] text-text-3 leading-[1.5]">{r.meta}</span>
      ),
    },
  ];

  return (
    <>
      {/* Recent activity card */}
      <Card className="p-[18px]">
        <div className="flex items-center justify-between pb-2.5 border-b border-border">
          <h3 className="text-[13px] font-semibold text-text m-0">
            Recent activity
          </h3>
          <MonoLabel>Last 6h · live</MonoLabel>
        </div>
        <ul className="list-none m-0 p-0 flex flex-col">
          {RECENT_ACTIVITY.map((item, i) => (
            <li
              key={i}
              className={cn(
                "flex items-start gap-2.5 py-2.5",
                i < RECENT_ACTIVITY.length - 1
                  ? "border-b border-dashed border-border"
                  : "",
              )}
            >
              <MonoLabel className="w-14 shrink-0 pt-px">{item.time}</MonoLabel>
              <span
                className={cn(
                  "w-1.5 h-1.5 rounded-full mt-[6px] shrink-0",
                  DOT[item.kind],
                )}
              />
              <div className="flex-1 min-w-0">
                <p className="text-[12px] text-text leading-[1.45] m-0">
                  {item.what}
                </p>
                <MonoLabel className="mt-0.5 block">{item.who}</MonoLabel>
              </div>
            </li>
          ))}
        </ul>
      </Card>

      {/* Audit log */}
      <SectionHead
        title="Audit log"
        sub="EVERY ACTION ACROSS THE ORG · JUMP TO ANY RESOURCE · 90-DAY RETENTION ON GROWTH"
        right={
          <>
            <Button variant="secondary" size="sm" icon={Filter}>
              Filters
            </Button>
            <Button variant="primary" size="sm" icon={Download}>
              Export CSV
            </Button>
          </>
        }
      />

      {/* Search bar */}
      <div className="bg-surface border border-border rounded-[9px] px-3 py-2 flex items-center gap-2.5">
        <Search size={14} strokeWidth={1.5} className="text-text-3 shrink-0" />
        <span className="text-[12px] text-text-3 flex-1">
          Search by resource — e.g. &quot;Living thermostat&quot;,
          &quot;SmartThings&quot;, &quot;vacant cool-down&quot;
        </span>
        <MonoLabel className="border border-border px-1.5 py-px rounded">
          ⌘ K
        </MonoLabel>
      </div>

      {/* Actor filter chips */}
      <div className="flex gap-1.5 flex-wrap">
        {ACTOR_FILTER_CHIPS.map(({ label, active }) => (
          <button
            key={label}
            className="border-0 p-0 bg-transparent cursor-pointer"
          >
            <Tag variant={active ? "graphite" : "neutral"}>{label}</Tag>
          </button>
        ))}
        <MonoLabel className="ml-auto self-center">
          showing {AUDIT.length} of 14,827 events · last 90 days
        </MonoLabel>
      </div>

      <DataTable columns={auditCols} rows={AUDIT} />
    </>
  );
}

// ─── API & webhooks tab ───────────────────────────────────────────────────────

const API_KEY_ROWS = [
  {
    name: "Reporting pipeline",
    preview: "ac_live_••••8j2k",
    scope: "read:portfolio",
    last: "today 07:30",
  },
  {
    name: "Internal CRM sync",
    preview: "ac_live_••••f3m1",
    scope: "read:stays",
    last: "yesterday",
  },
];
type ApiKeyRow = (typeof API_KEY_ROWS)[number];
const API_KEY_COLS: TableColumn<ApiKeyRow>[] = [
  { k: "name", label: "Name", w: "1fr" },
  {
    k: "preview",
    label: "Preview",
    w: "1fr",
    render: (r) => (
      <span className="font-mono text-[12px] text-text-3">{r.preview}</span>
    ),
  },
  { k: "scope", label: "Scope", w: "1fr" },
  {
    k: "last",
    label: "Last used",
    w: "1fr",
    render: (r) => <MonoLabel>{r.last}</MonoLabel>,
  },
  {
    k: "act",
    label: "",
    w: "80px",
    align: "right",
    render: () => (
      <Button variant="ghost" size="sm">
        Revoke
      </Button>
    ),
  },
];

function ApiTab() {
  return (
    <>
      <SettingsCard
        title="Webhooks · outbound"
        sub="Subscribe your services to events from Alphacon. Coming in 1.5."
      >
        <div className="p-[18px] border border-dashed border-border rounded-[9px] text-center text-[12px] text-text-3">
          Outbound webhooks not available on the Growth plan. Available on Scale
          and above.
        </div>
      </SettingsCard>

      <SettingsCard
        title="API keys"
        sub="Server-to-server access for your own dashboards or imports."
        footer={
          <Button variant="primary" size="sm" icon={Plus}>
            Generate key
          </Button>
        }
      >
        <DataTable columns={API_KEY_COLS} rows={API_KEY_ROWS} />
      </SettingsCard>
    </>
  );
}

// ─── Agent tab ────────────────────────────────────────────────────────────────

const MODEL_TIERS = [
  {
    tier: "HAIKU",
    label: "Haiku 4.5",
    use: "Status lookups · single tool",
    cost: "£0.001 / msg",
    on: true,
    recommended: false,
  },
  {
    tier: "SONNET",
    label: "Sonnet 4.6",
    use: "Reasoning · multi-step plans",
    cost: "£0.012 / msg",
    on: true,
    recommended: true,
  },
  {
    tier: "OPUS",
    label: "Opus 4.5",
    use: "Complex analytics · escalated",
    cost: "£0.090 / msg",
    on: false,
    recommended: false,
  },
];

const CONFIRMATIONS = [
  {
    l: "Unlock a door",
    always: true,
    desc: "Always require approval — physical security.",
  },
  {
    l: "Change thermostat",
    always: false,
    desc: "Approve when delta > 4°C or unit is occupied.",
  },
  { l: "Send a guest message", always: true, desc: "Always preview drafts." },
  {
    l: "Cancel or refund a stay",
    always: true,
    desc: "Always require approval.",
  },
  {
    l: "Acknowledge an automation run",
    always: false,
    desc: "Approve only when an action failed.",
  },
];

function AgentTab() {
  return (
    <>
      <SettingsCard
        title="Routing"
        sub="The agent picks a model tier based on the question's complexity. You can lock the floor."
      >
        <div className="grid grid-cols-3 gap-3">
          {MODEL_TIERS.map((m) => (
            <div
              key={m.tier}
              className={cn(
                "p-4 rounded-card border",
                m.recommended
                  ? "bg-bg border-graphite"
                  : "bg-surface border-border",
              )}
            >
              <div className="flex items-center justify-between">
                <MonoLabel>{m.tier}</MonoLabel>
                <Tag variant={m.on ? "ok" : "neutral"} withDot>
                  {m.on ? "on" : "off"}
                </Tag>
              </div>
              <p className="font-serif text-[18px] text-text mt-2 m-0">
                {m.label}
              </p>
              <p className="text-[12px] text-text-2 mt-1.5 leading-[1.5] m-0">
                {m.use}
              </p>
              <MonoLabel className="mt-2.5 block">{m.cost}</MonoLabel>
            </div>
          ))}
        </div>
      </SettingsCard>

      <SettingsCard
        title="Personas"
        sub="The operator persona powers the console. Guest-facing personas arrive with the tenant app."
      >
        <div className="flex justify-between items-center py-3 border-b border-border">
          <div>
            <p className="text-[13px] font-medium text-text m-0">Operator</p>
            <p className="text-[12px] text-text-3 mt-1 m-0">
              Professional · expects precision and minimal hedging. Sees all
              property-owned devices and data.
            </p>
          </div>
          <Button variant="ghost" size="sm">
            Edit prompt
          </Button>
        </div>
        <div className="flex justify-between items-center py-3 opacity-55">
          <div>
            <p className="text-[13px] font-medium text-text m-0">
              Concierge · Home Assistant
            </p>
            <p className="text-[12px] text-text-3 mt-1 m-0">
              Guest and resident personas — ship with the tenant app in a later
              release.
            </p>
          </div>
          <Tag variant="neutral">coming soon</Tag>
        </div>
      </SettingsCard>

      <SettingsCard
        title="Confirmations"
        sub="Which actions require a human OK before the agent runs them."
      >
        {CONFIRMATIONS.map((c) => (
          <div
            key={c.l}
            className="flex justify-between items-center py-3 border-b border-border last:border-0"
          >
            <div className="max-w-[480px]">
              <p className="text-[13px] font-medium text-text m-0">{c.l}</p>
              <p className="text-[12px] text-text-3 mt-1 m-0">{c.desc}</p>
            </div>
            <Tag variant={c.always ? "graphite" : "neutral"}>
              {c.always ? "always confirm" : "rule-based"}
            </Tag>
          </div>
        ))}
      </SettingsCard>
    </>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

const TABS = [
  { id: "organization", label: "Organization" },
  { id: "portfolios", label: "Portfolios", count: 2 },
  { id: "billing", label: "Billing" },
  { id: "security", label: "Security" },
  { id: "audit", label: "Audit log" },
  { id: "api", label: "API & webhooks" },
  { id: "agent", label: "Agent" },
];

export function SettingsScreen() {
  const [tab, setTab] = useState("organization");
  const isAudit = tab === "audit";

  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Settings"
        sub="Organization, billing, security, audit log, and developer settings"
      />

      <div className="px-7 border-b border-border bg-surface">
        <Tabs value={tab} onChange={setTab} tabs={TABS} />
      </div>

      <div
        className={cn(
          "px-7 pt-5 pb-8 flex flex-col gap-5",
          isAudit ? "max-w-[1200px]" : "max-w-[920px]",
        )}
      >
        {tab === "organization" && <OrgTab />}
        {tab === "portfolios" && <PortfoliosTab />}
        {tab === "billing" && <BillingTab />}
        {tab === "security" && <SecurityTab />}
        {tab === "audit" && <AuditTab />}
        {tab === "api" && <ApiTab />}
        {tab === "agent" && <AgentTab />}
      </div>
    </>
  );
}
