"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { motion } from "framer-motion";
import { User, Bell, Cable, CreditCard, Users, Save } from "lucide-react";
import * as RadixTabs from "@radix-ui/react-tabs";
import { PageWrapper, Switch, Button } from "@/themes";
import { useIntegrations } from "@/hooks/useIntegrations";
import { cn } from "@/lib/utils";

const TABS = [
  { value: "account", label: "Account", icon: User },
  { value: "notifications", label: "Notifications", icon: Bell },
  { value: "integrations", label: "Integrations", icon: Cable },
  { value: "billing", label: "Billing", icon: CreditCard },
  { value: "team", label: "Team", icon: Users },
];

function AccountTab() {
  return (
    <div className="space-y-6">
      <div className="bg-surface border border-border rounded-xl p-5">
        <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-4">Profile</p>
        <div className="flex items-center gap-4 mb-5">
          <div className="w-12 h-12 rounded-full bg-graphite flex items-center justify-center text-surface font-mono">A</div>
          <div>
            <p className="font-body font-normal text-sm text-text">Alphacon Demo</p>
            <p className="font-mono text-xs text-text-3">demo@alphacon.ai</p>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[
            { label: "Display Name", value: "Alphacon Demo" },
            { label: "Email", value: "demo@alphacon.ai" },
            { label: "Organisation", value: "Alphacon Properties Ltd" },
            { label: "Role", value: "Owner" },
          ].map((f) => (
            <div key={f.label}>
              <label className="font-body font-normal text-xs text-text-3 uppercase tracking-wider block mb-1.5">{f.label}</label>
              <input
                defaultValue={f.value}
                readOnly
                className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2 font-body text-sm text-text focus:outline-none focus:border-border-strong"
              />
            </div>
          ))}
        </div>
        <div className="mt-4 flex justify-end">
          <Button onClick={() => toast.success("Profile saved")}>
            <Save size={13} className="mr-1.5" />
            Save changes
          </Button>
        </div>
      </div>

      <div className="bg-surface border border-border rounded-xl p-5">
        <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-4">Password</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="font-body font-normal text-xs text-text-3 uppercase tracking-wider block mb-1.5">Current Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2 font-body text-sm text-text focus:outline-none focus:border-border-strong placeholder:text-text-3"
            />
          </div>
          <div>
            <label className="font-body font-normal text-xs text-text-3 uppercase tracking-wider block mb-1.5">New Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2 font-body text-sm text-text focus:outline-none focus:border-border-strong placeholder:text-text-3"
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end">
          <Button onClick={() => toast.success("Password updated")}>Update Password</Button>
        </div>
      </div>
    </div>
  );
}

const NOTIFICATION_PREFS = [
  { key: "critical_alerts", label: "Critical Alerts", description: "Immediate notification for critical device failures or leaks" },
  { key: "warning_alerts", label: "Warning Alerts", description: "Notifications for warning-level events" },
  { key: "weekly_digest", label: "Weekly Digest", description: "Weekly summary of energy usage and property health" },
  { key: "device_offline", label: "Device Offline", description: "Notify when a device goes offline for more than 30 minutes" },
  { key: "maintenance_reminders", label: "Maintenance Reminders", description: "Upcoming scheduled maintenance tasks" },
];

function NotificationsTab() {
  const [prefs, setPrefs] = useState<Record<string, boolean>>(() => {
    if (typeof window === "undefined") return {};
    try {
      return JSON.parse(localStorage.getItem("notification_prefs") ?? "{}");
    } catch {
      return {};
    }
  });

  function toggle(key: string) {
    setPrefs((p) => {
      const next = { ...p, [key]: !p[key] };
      localStorage.setItem("notification_prefs", JSON.stringify(next));
      toast.success("Preference saved");
      return next;
    });
  }

  return (
    <div className="bg-surface border border-border rounded-xl divide-y divide-border">
      {NOTIFICATION_PREFS.map((pref) => (
        <div key={pref.key} className="flex items-center justify-between px-5 py-4">
          <div>
            <p className="font-body font-normal text-sm text-text">{pref.label}</p>
            <p className="font-body font-light text-xs text-text-3 mt-0.5">{pref.description}</p>
          </div>
          <Switch
            checked={prefs[pref.key] ?? (pref.key === "critical_alerts")}
            onCheckedChange={() => toggle(pref.key)}
          />
        </div>
      ))}
    </div>
  );
}

function IntegrationsTab() {
  const { data: integrations = [], isLoading } = useIntegrations();

  return (
    <div className="space-y-3">
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-surface border border-border rounded-xl h-16 animate-pulse" />
          ))}
        </div>
      ) : (
        integrations.map((integration) => (
          <div key={integration.vendor} className="bg-surface border border-border rounded-xl flex items-center justify-between px-5 py-4">
            <div>
              <p className="font-body font-normal text-sm text-text">{integration.display_name}</p>
              <p className="font-body font-light text-xs text-text-3 mt-0.5">{integration.description}</p>
            </div>
            <span className={cn(
              "font-mono text-xs px-2.5 py-1 rounded-full border",
              integration.connected
                ? "text-green bg-green-bg border-green/20"
                : "text-text-3 bg-surface-2 border-border"
            )}>
              {integration.connected ? "Connected" : "Not connected"}
            </span>
          </div>
        ))
      )}
      <p className="font-body font-light text-xs text-text-3 text-center pt-2">
        Manage API keys and connection settings via the{" "}
        <a href="/integrations" className="underline hover:text-text-2">Integrations</a> page.
      </p>
    </div>
  );
}

function BillingTab() {
  return (
    <div className="space-y-4">
      <div className="bg-surface border border-border rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3">Current Plan</p>
          <span className="font-mono text-xs bg-surface-2 border border-border text-text-3 px-2 py-0.5 rounded-full">Free</span>
        </div>
        <p className="font-display italic text-2xl text-text mb-1">Free</p>
        <p className="font-body font-light text-sm text-text-3 mb-5">Up to 3 properties, 20 devices, basic analytics</p>
        <Button onClick={() => toast.success("Upgrade flow coming soon!")}>Upgrade to Pro</Button>
      </div>
      <div className="bg-surface border border-border rounded-xl p-5">
        <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-3">Pro Plan Features</p>
        <ul className="space-y-2">
          {[
            "Unlimited properties and devices",
            "AI-powered predictive maintenance",
            "Advanced energy analytics",
            "Priority support",
            "Custom report templates",
            "API access",
          ].map((f) => (
            <li key={f} className="flex items-center gap-2.5 font-body font-light text-sm text-text-2">
              <span className="w-1.5 h-1.5 rounded-full bg-graphite flex-shrink-0" />
              {f}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function TeamTab() {
  return (
    <div className="space-y-4">
      <div className="bg-surface border border-border rounded-xl divide-y divide-border">
        {[
          { name: "Alphacon Demo", email: "demo@alphacon.ai", role: "Owner" },
        ].map((member) => (
          <div key={member.email} className="flex items-center gap-3 px-5 py-4">
            <div className="w-8 h-8 rounded-full bg-graphite flex items-center justify-center text-surface text-xs font-mono flex-shrink-0">
              {member.name[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-body font-normal text-sm text-text">{member.name}</p>
              <p className="font-mono text-xs text-text-3">{member.email}</p>
            </div>
            <span className="font-mono text-xs bg-surface-2 border border-border text-text-3 px-2 py-0.5 rounded-full">
              {member.role}
            </span>
          </div>
        ))}
      </div>
      <Button variant="secondary" onClick={() => toast.success("Team invite coming in Pro plan!")}>
        Invite team member
      </Button>
    </div>
  );
}

export default function SettingsPage() {
  const [tab, setTab] = useState("account");

  return (
    <PageWrapper>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="p-6 md:p-8 max-w-3xl mx-auto"
      >
        <div className="mb-6">
          <h1 className="font-display italic text-2xl text-text">Settings</h1>
          <p className="font-body font-light text-sm text-text-3 mt-1">Manage your account and preferences</p>
        </div>

        <RadixTabs.Root value={tab} onValueChange={setTab}>
          <RadixTabs.List className="flex items-center gap-1 border-b border-border mb-6 -mx-1 px-1 overflow-x-auto">
            {TABS.map(({ value, label, icon: Icon }) => (
              <RadixTabs.Trigger
                key={value}
                value={value}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-2.5 text-xs font-body font-light whitespace-nowrap border-b-2 transition-colors -mb-px",
                  tab === value
                    ? "border-graphite text-text"
                    : "border-transparent text-text-3 hover:text-text-2"
                )}
              >
                <Icon size={12} />
                {label}
              </RadixTabs.Trigger>
            ))}
          </RadixTabs.List>

          <RadixTabs.Content value="account"><AccountTab /></RadixTabs.Content>
          <RadixTabs.Content value="notifications"><NotificationsTab /></RadixTabs.Content>
          <RadixTabs.Content value="integrations"><IntegrationsTab /></RadixTabs.Content>
          <RadixTabs.Content value="billing"><BillingTab /></RadixTabs.Content>
          <RadixTabs.Content value="team"><TeamTab /></RadixTabs.Content>
        </RadixTabs.Root>
      </motion.div>
    </PageWrapper>
  );
}
