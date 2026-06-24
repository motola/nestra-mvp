"use client";

import { useRef, useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import {
  AlertTriangle,
  Bell,
  CheckCircle,
  ChevronRight,
  FlaskConical,
  LogOut,
  Menu,
  Search,
  X,
  XCircle,
} from "lucide-react";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { format } from "date-fns";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useAlerts, useDismissAlert } from "@/hooks/useAlerts";
import { cn } from "@/lib/utils";
import { useSidebar } from "@/contexts/SidebarContext";
import { useAuth } from "@/contexts/AuthContext";
import { propertiesApi, devicesApi, getShowDemo, setShowDemo } from "@/lib/api";
import type { Alert, AlertSeverity } from "@/lib/types";

const SEVERITY_ICON: Record<AlertSeverity, typeof CheckCircle> = {
  critical: XCircle,
  warning: AlertTriangle,
  info: CheckCircle,
};
const SEVERITY_COL: Record<AlertSeverity, string> = {
  critical: "text-red",
  warning: "text-amber",
  info: "text-green",
};

const SEGMENT_LABELS: Record<string, string> = {
  dashboard: "Dashboard",
  portfolio: "Portfolio",
  properties: "Portfolio",
  alerts: "Alerts",
  intelligence: "Intelligence",
  devices: "Devices",
  reports: "Reports",
  tenants: "Tenants",
  maintenance: "Maintenance",
  integrations: "Integrations",
  settings: "Settings",
};

type Crumb = { label: string; href?: string };

function CrumbNav({ crumbs }: { crumbs: Crumb[] }) {
  return (
    <nav className="flex items-center gap-1.5 text-sm">
      {crumbs.map((crumb, i) => (
        <span key={i} className="flex items-center gap-1.5">
          {i > 0 && <ChevronRight size={13} className="text-text-3" />}
          {crumb.href ? (
            <a
              href={crumb.href}
              className="font-body font-light text-text-3 hover:text-text-2 transition-colors"
            >
              {crumb.label}
            </a>
          ) : (
            <span className="font-body font-normal text-text">
              {crumb.label}
            </span>
          )}
        </span>
      ))}
    </nav>
  );
}

function Breadcrumb() {
  const pathname = usePathname();

  // Match /properties/{id} or /properties/{id}/devices/{deviceId}
  const propMatch = pathname.match(
    /^\/properties\/([^/]+)(?:\/devices\/([^/]+))?/,
  );
  const propertyId = propMatch?.[1] ?? null;
  const deviceId = propMatch?.[2] ?? null;

  const { data: property } = useQuery({
    queryKey: ["property", propertyId],
    queryFn: () => propertiesApi.get(propertyId!),
    enabled: Boolean(propertyId),
    staleTime: 60_000,
  });

  const { data: device } = useQuery({
    queryKey: ["device-header", deviceId],
    queryFn: () => devicesApi.get(deviceId!),
    enabled: Boolean(deviceId),
    staleTime: 60_000,
  });

  if (propertyId) {
    const crumbs: Crumb[] = [
      { label: "Portfolio", href: "/portfolio" },
      {
        label: property?.name ?? "...",
        href: deviceId ? `/properties/${propertyId}` : undefined,
      },
      ...(deviceId ? [{ label: device?.name ?? "..." } as Crumb] : []),
    ];
    return <CrumbNav crumbs={crumbs} />;
  }

  const segments = pathname.split("/").filter(Boolean);
  if (segments.length === 0)
    return <span className="font-body text-sm text-text-2">Dashboard</span>;

  const crumbs: Crumb[] = segments.map((seg, i) => ({
    label: SEGMENT_LABELS[seg] ?? seg,
    href:
      i < segments.length - 1
        ? "/" + segments.slice(0, i + 1).join("/")
        : undefined,
  }));

  return <CrumbNav crumbs={crumbs} />;
}

function NotificationPanel({
  alerts,
  onClose,
}: {
  alerts: Alert[];
  onClose: () => void;
}) {
  const router = useRouter();
  const dismiss = useDismissAlert();
  const ref = useRef<HTMLDivElement>(null);
  const active = alerts.filter((a) => !a.dismissed);

  useEffect(() => {
    function h(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    }
    document.addEventListener("mousedown", h);
    return () => document.removeEventListener("mousedown", h);
  }, [onClose]);

  return (
    <div
      ref={ref}
      className="absolute top-12 right-0 w-80 bg-surface/90 backdrop-blur-xl border border-border rounded-xl z-50 overflow-hidden shadow-lg shadow-graphite/5"
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <p className="font-body font-normal text-sm text-text">Notifications</p>
        <div className="flex items-center gap-3">
          {active.length > 0 && (
            <button
              onClick={() => active.forEach((a) => dismiss.mutate(a.id))}
              className="font-body font-light text-xs text-text-3 hover:text-text-2 transition-colors"
            >
              Mark all read
            </button>
          )}
          <button onClick={onClose} className="text-text-3 hover:text-text-2">
            <X size={14} />
          </button>
        </div>
      </div>

      {active.length === 0 ? (
        <div className="px-4 py-8 text-center">
          <p className="font-body font-light text-sm text-text-3">
            No active alerts
          </p>
        </div>
      ) : (
        <>
          <ul className="max-h-80 overflow-y-auto divide-y divide-border">
            {active.map((alert) => {
              const Icon = SEVERITY_ICON[alert.severity];
              return (
                <li
                  key={alert.id}
                  className="px-4 py-3 hover:bg-surface-2 transition-colors group"
                >
                  <div className="flex items-start gap-2.5">
                    <Icon
                      size={14}
                      className={cn(
                        "flex-shrink-0 mt-0.5",
                        SEVERITY_COL[alert.severity],
                      )}
                    />
                    <div className="flex-1 min-w-0">
                      <button
                        onClick={() => {
                          router.push(
                            `/properties/${alert.property_id}/devices/${alert.device_id}`,
                          );
                          onClose();
                        }}
                        className="font-body text-xs text-text leading-snug text-left hover:text-text-2 w-full block"
                      >
                        {alert.message}
                      </button>
                      <div className="flex items-center justify-between mt-1">
                        <p className="font-mono text-xs text-text-3 truncate">
                          {alert.device_name}
                        </p>
                        <p className="font-mono text-xs text-text-3 ml-2 flex-shrink-0">
                          {format(new Date(alert.created_at), "d MMM, HH:mm")}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => dismiss.mutate(alert.id)}
                      className="text-text-3 hover:text-text-2 opacity-0 group-hover:opacity-100 transition-all"
                    >
                      <X size={12} />
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
          <div className="px-4 py-2.5 border-t border-border">
            <a
              href="/alerts"
              onClick={onClose}
              className="font-body font-light text-xs text-text-3 hover:text-text-2 transition-colors"
            >
              View all alerts →
            </a>
          </div>
        </>
      )}
    </div>
  );
}

export function Header() {
  const { toggle } = useSidebar();
  const { user, logout } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: alerts = [] } = useAlerts();
  const [notifOpen, setNotifOpen] = useState(false);
  const [showDemo, setShowDemoState] = useState(false);
  useEffect(() => setShowDemoState(getShowDemo()), []);
  const activeAlerts = alerts.filter((a) => !a.dismissed).length;
  const initial = user?.full_name?.trim()?.[0]?.toUpperCase() ?? "?";

  function handleSignOut() {
    logout();
    router.push("/login");
  }

  function toggleDemo() {
    const next = !showDemo;
    setShowDemo(next);
    setShowDemoState(next);
    // Refetch everything so demo data appears/disappears across the app.
    queryClient.invalidateQueries();
  }

  return (
    <header className="h-14 flex-shrink-0 bg-surface/70 backdrop-blur-xl border-b border-border flex items-center justify-between px-4 md:px-6 sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <button
          onClick={toggle}
          className="md:hidden text-text-3 hover:text-text transition-colors"
        >
          <Menu size={18} />
        </button>
        <Breadcrumb />
      </div>

      <div className="flex items-center gap-2">
        {/* Search */}
        <button
          onClick={() => {
            const e = new KeyboardEvent("keydown", {
              key: "k",
              metaKey: true,
              bubbles: true,
            });
            document.dispatchEvent(e);
          }}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-2 border border-border text-text-3 hover:text-text-2 hover:border-border-strong transition-colors text-sm font-body font-light"
        >
          <Search size={13} />
          <span className="hidden sm:inline">Search</span>
          <kbd className="hidden sm:inline font-mono text-xs bg-surface border border-border px-1.5 py-0.5 rounded ml-1">
            ⌘K
          </kbd>
        </button>

        {/* Bell */}
        <div className="relative">
          <button
            onClick={() => setNotifOpen((v) => !v)}
            className="relative w-8 h-8 flex items-center justify-center text-text-3 hover:text-text hover:bg-surface-2 rounded-lg transition-colors"
          >
            <Bell size={16} />
            {activeAlerts > 0 && (
              <span className="absolute top-1 right-1 w-3.5 h-3.5 bg-red rounded-full text-surface text-[9px] font-mono flex items-center justify-center">
                {activeAlerts > 9 ? "9+" : activeAlerts}
              </span>
            )}
          </button>
          {notifOpen && (
            <NotificationPanel
              alerts={alerts}
              onClose={() => setNotifOpen(false)}
            />
          )}
        </div>

        {/* Avatar dropdown */}
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button className="w-8 h-8 rounded-full bg-graphite flex items-center justify-center text-surface text-xs font-mono hover:bg-graphite-2 transition-colors">
              {initial}
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content
              align="end"
              sideOffset={8}
              className="w-52 bg-surface/90 backdrop-blur-xl border border-border rounded-xl z-50 overflow-hidden shadow-lg shadow-graphite/5"
            >
              <div className="px-4 py-3 border-b border-border">
                <p className="font-body font-normal text-sm text-text">
                  {user?.organization?.name ?? user?.full_name ?? "Account"}
                </p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="font-mono text-xs text-text-3 truncate">
                    {user?.email ?? ""}
                  </span>
                </div>
              </div>
              <div className="border-t border-border py-1">
                <DropdownMenu.Item
                  onSelect={(e) => {
                    e.preventDefault();
                    toggleDemo();
                  }}
                  className="flex items-center justify-between gap-2.5 px-4 py-2 text-sm font-body text-text-2 hover:bg-surface-2 hover:text-text cursor-pointer outline-none"
                >
                  <span className="flex items-center gap-2.5">
                    <FlaskConical size={14} />
                    Show demo data
                  </span>
                  <span
                    className={cn(
                      "font-mono text-xs px-1.5 py-0.5 rounded-full border",
                      showDemo
                        ? "bg-amber-bg text-amber border-amber/20"
                        : "bg-surface-2 text-text-3 border-border",
                    )}
                  >
                    {showDemo ? "On" : "Off"}
                  </span>
                </DropdownMenu.Item>
              </div>
              <div className="border-t border-border py-1">
                <DropdownMenu.Item
                  onSelect={handleSignOut}
                  className="flex items-center gap-2.5 px-4 py-2 text-sm font-body text-red hover:bg-red-bg cursor-pointer outline-none"
                >
                  <LogOut size={14} />
                  Sign out
                </DropdownMenu.Item>
              </div>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      </div>
    </header>
  );
}
