"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import {
  Bell,
  Brain,
  Building2,
  Cable,
  LayoutGrid,
  Search,
  Settings,
  Zap,
} from "lucide-react";
import { useProperties } from "@/hooks/useProperty";
import { useAlerts } from "@/hooks/useAlerts";
import { cn } from "@/lib/utils";

const PAGES = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutGrid },
  { label: "Portfolio", href: "/portfolio", icon: Building2 },
  { label: "Alerts", href: "/alerts", icon: Bell },
  { label: "Intelligence", href: "/intelligence", icon: Brain },
  { label: "Devices", href: "/devices", icon: Zap },
  { label: "Reports", href: "/reports", icon: Zap },
  { label: "Integrations", href: "/integrations", icon: Cable },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const router = useRouter();
  const { data: properties = [] } = useProperties();
  const { data: alerts = [] } = useAlerts();
  const activeAlerts = alerts.filter((a) => !a.dismissed);

  useEffect(() => {
    function handler(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((v) => !v);
      }
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  function navigate(href: string) {
    router.push(href);
    setOpen(false);
    setQuery("");
  }

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center pt-[20vh]"
      onClick={() => setOpen(false)}
    >
      <div className="absolute inset-0 bg-graphite/30 backdrop-blur-sm" />
      <div
        className="relative w-full max-w-lg bg-surface border border-border rounded-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <Command className="w-full" shouldFilter={true}>
          <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
            <Search size={15} className="text-text-3 flex-shrink-0" />
            <Command.Input
              value={query}
              onValueChange={setQuery}
              placeholder="Search properties, devices, pages…"
              className="flex-1 bg-transparent font-body text-sm text-text placeholder:text-text-3 focus:outline-none"
              autoFocus
            />
            <kbd className="font-mono text-xs text-text-3 bg-surface-2 border border-border px-1.5 py-0.5 rounded">
              Esc
            </kbd>
          </div>

          <Command.List className="max-h-80 overflow-y-auto p-2">
            <Command.Empty className="py-8 text-center font-body font-light text-sm text-text-3">
              No results found.
            </Command.Empty>

            {properties.length > 0 && (
              <Command.Group
                heading={
                  <span className="font-mono text-xs text-text-3 uppercase tracking-widest px-2 py-1 block">
                    Properties
                  </span>
                }
              >
                {properties.map((p) => (
                  <Command.Item
                    key={p.id}
                    value={`property-${p.name}`}
                    onSelect={() => navigate(`/properties/${p.id}`)}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer",
                      "font-body text-sm text-text-2 hover:text-text hover:bg-surface-2",
                      "data-[selected=true]:bg-surface-2 data-[selected=true]:text-text",
                    )}
                  >
                    <Building2 size={14} className="text-text-3" />
                    {p.name}
                    <span className="ml-auto font-mono text-xs text-text-3">
                      {p.address.split(",")[1]?.trim()}
                    </span>
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {activeAlerts.length > 0 && (
              <Command.Group
                heading={
                  <span className="font-mono text-xs text-text-3 uppercase tracking-widest px-2 py-1 block">
                    Active Alerts
                  </span>
                }
              >
                {activeAlerts.slice(0, 5).map((a) => (
                  <Command.Item
                    key={a.id}
                    value={`alert-${a.message}`}
                    onSelect={() =>
                      navigate(
                        `/properties/${a.property_id}/devices/${a.device_id}`,
                      )
                    }
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer",
                      "font-body text-sm text-text-2 hover:text-text hover:bg-surface-2",
                      "data-[selected=true]:bg-surface-2",
                    )}
                  >
                    <Bell size={14} className="text-amber" />
                    <span className="truncate">
                      {a.device_name} — {a.message}
                    </span>
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            <Command.Group
              heading={
                <span className="font-mono text-xs text-text-3 uppercase tracking-widest px-2 py-1 block">
                  Pages
                </span>
              }
            >
              {PAGES.map(({ label, href, icon: Icon }) => (
                <Command.Item
                  key={href}
                  value={`page-${label}`}
                  onSelect={() => navigate(href)}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer",
                    "font-body text-sm text-text-2 hover:text-text hover:bg-surface-2",
                    "data-[selected=true]:bg-surface-2 data-[selected=true]:text-text",
                  )}
                >
                  <Icon size={14} className="text-text-3" />
                  {label}
                </Command.Item>
              ))}
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
