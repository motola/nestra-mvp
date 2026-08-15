"use client"; // Client: tab switching

import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs } from "@/components/ui/tabs";
import { Card, SectionHead } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { cn } from "@/lib/cn";

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
            <TextInput value="" />
          </Field>
          <Field label="Legal name">
            <TextInput value="" />
          </Field>
          <Field label="URL slug" hint="yourorg.nestra.com">
            <TextInput value="" />
          </Field>
          <Field label="Default timezone">
            <SelectInput
              value="UTC"
              options={["Europe/London", "Europe/Paris", "UTC", "US/Eastern"]}
            />
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
      <div className="text-center py-12 text-text-3">
        <p className="text-[13px]">
          No portfolios yet. Create your first portfolio to get started.
        </p>
      </div>
    </>
  );
}

// ─── Billing tab ──────────────────────────────────────────────────────────────

function BillingTab() {
  return (
    <>
      <div className="text-center py-12 text-text-3">
        <p className="text-[13px]">
          Billing information will appear here once you create your first
          portfolio.
        </p>
      </div>
    </>
  );
}

// ─── Security tab ─────────────────────────────────────────────────────────────

function SecurityTab() {
  return (
    <>
      <div className="text-center py-12 text-text-3">
        <p className="text-[13px]">
          Security settings will appear once your organization is set up.
        </p>
      </div>
    </>
  );
}

// ─── Audit log tab ────────────────────────────────────────────────────────────

function AuditTab() {
  return (
    <>
      <div className="text-center py-12 text-text-3">
        <p className="text-[13px]">
          No audit log yet. Organization activity will appear here.
        </p>
      </div>
    </>
  );
}

// ─── API & webhooks tab ───────────────────────────────────────────────────────

function ApiTab() {
  return (
    <>
      <div className="text-center py-12 text-text-3">
        <p className="text-[13px]">
          API keys and webhooks will be available soon.
        </p>
      </div>
    </>
  );
}

// ─── Agent tab ────────────────────────────────────────────────────────────────

function AgentTab() {
  return (
    <>
      <div className="text-center py-12 text-text-3">
        <p className="text-[13px]">
          Agent settings and model routing will be available soon.
        </p>
      </div>
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
