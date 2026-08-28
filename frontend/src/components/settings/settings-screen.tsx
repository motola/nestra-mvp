"use client"; // Client: tab switching

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Tabs } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { useAuth } from "@/lib/auth/provider";
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

function TextInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent"
    />
  );
}

function SelectInput({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (value: string) => void;
  options: string[];
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
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

function OrgTab({
  displayName,
  legalName,
  slug,
  organizationId,
}: {
  displayName: string;
  legalName: string;
  slug: string;
  organizationId: string;
}) {
  const [formData, setFormData] = useState({
    name: displayName,
    slug: slug,
    timezone: "UTC",
  });
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const handleSave = async () => {
    setIsSaving(true);
    setMessage(null);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${apiUrl}/organizations/${organizationId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
          body: JSON.stringify(formData),
        },
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      setMessage({ type: "success", text: "Settings saved successfully" });
    } catch (error) {
      const errMsg = error instanceof Error ? error.message : "Failed to save";
      setMessage({ type: "error", text: errMsg });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      {message && (
        <div
          className={`mb-4 px-4 py-2 rounded-lg text-sm font-medium ${
            message.type === "success"
              ? "bg-green-100 text-green-700"
              : "bg-red-100 text-red-700"
          }`}
        >
          {message.text}
        </div>
      )}
      <SettingsCard
        title="Organization profile"
        sub="Visible to teammates. Tenants see only the display name."
        footer={
          <Button
            variant="primary"
            size="sm"
            onClick={handleSave}
            disabled={isSaving}
          >
            {isSaving ? "Saving..." : "Save changes"}
          </Button>
        }
      >
        <div className="grid grid-cols-2 gap-3.5">
          <Field label="Display name">
            <TextInput
              value={formData.name}
              onChange={(val) => setFormData({ ...formData, name: val })}
            />
          </Field>
          <Field label="Legal name">
            <TextInput value={legalName} onChange={() => {}} />
          </Field>
          <Field label="URL slug" hint="yourorg.nestra.com">
            <TextInput
              value={formData.slug}
              onChange={(val) => setFormData({ ...formData, slug: val })}
            />
          </Field>
          <Field label="Default timezone">
            <SelectInput
              value={formData.timezone}
              onChange={(val) => setFormData({ ...formData, timezone: val })}
              options={["Europe/London", "Europe/Paris", "UTC", "US/Eastern"]}
            />
          </Field>
        </div>
      </SettingsCard>
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
  { id: "billing", label: "Billing" },
  { id: "security", label: "Security" },
  { id: "audit", label: "Audit log" },
  { id: "api", label: "API & webhooks" },
  { id: "agent", label: "Agent" },
];

export function SettingsScreen() {
  const [tab, setTab] = useState("organization");
  const isAudit = tab === "audit";
  const { organization } = useAuth();

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
        {tab === "organization" && (
          <OrgTab
            displayName={organization?.name || ""}
            legalName={organization?.name || ""}
            slug={organization?.slug || ""}
            organizationId={organization?.id || ""}
          />
        )}
        {tab === "billing" && <BillingTab />}
        {tab === "security" && <SecurityTab />}
        {tab === "audit" && <AuditTab />}
        {tab === "api" && <ApiTab />}
        {tab === "agent" && <AgentTab />}
      </div>
    </>
  );
}
