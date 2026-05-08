"use client";

import { useState } from "react";
import { AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { useAlerts, useDismissAlert } from "@/hooks/useAlerts";
import type { AlertSeverity } from "@/lib/types";
import { cn } from "@/lib/utils";
import { PageWrapper, AlertCard, SkeletonCard, EmptyState } from "@/themes";

type Filter = "all" | AlertSeverity;

const FILTER_TABS: { key: Filter; label: string }[] = [
  { key: "all", label: "All" },
  { key: "critical", label: "Critical" },
  { key: "warning", label: "Warning" },
  { key: "info", label: "Info" },
];

const SEVERITY_HEADER: Record<AlertSeverity, { label: string; icon: typeof CheckCircle; color: string }> = {
  critical: { label: "Critical", icon: XCircle, color: "text-red" },
  warning: { label: "Warning", icon: AlertTriangle, color: "text-amber" },
  info: { label: "Info", icon: CheckCircle, color: "text-green" },
};

function StatPill({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color?: string;
}) {
  return (
    <div className="bg-surface border border-border rounded-xl p-4 flex flex-col gap-1">
      <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3">{label}</p>
      <p className={cn("font-mono text-2xl", color ?? "text-text")}>{value}</p>
    </div>
  );
}

export default function AlertsPage() {
  const { data: alerts = [], isLoading } = useAlerts();
  const dismiss = useDismissAlert();
  const [filter, setFilter] = useState<Filter>("all");

  const active = alerts.filter((a) => !a.dismissed);
  const filtered = filter === "all" ? active : active.filter((a) => a.severity === filter);

  const counts: Record<Filter, number> = {
    all: active.length,
    critical: active.filter((a) => a.severity === "critical").length,
    warning: active.filter((a) => a.severity === "warning").length,
    info: active.filter((a) => a.severity === "info").length,
  };

  return (
    <PageWrapper>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="p-6 md:p-8 max-w-7xl mx-auto"
      >
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="font-display italic text-2xl text-text">Alerts</h1>
            <p className="font-body font-light text-sm text-text-3 mt-1">
              {isLoading ? "Loading…" : `${active.length} active alert${active.length !== 1 ? "s" : ""}`}
            </p>
          </div>
          {active.length > 0 && (
            <button
              onClick={() => active.forEach((a) => dismiss.mutate(a.id))}
              className="font-body font-light text-sm text-text-3 hover:text-text-2 transition-colors mt-1"
            >
              Dismiss all
            </button>
          )}
        </div>

        {/* Stats row */}
        {!isLoading && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
            <StatPill label="Total" value={counts.all} />
            <StatPill label="Critical" value={counts.critical} color={counts.critical > 0 ? "text-red" : undefined} />
            <StatPill label="Warning" value={counts.warning} color={counts.warning > 0 ? "text-amber" : undefined} />
            <StatPill label="Info" value={counts.info} color={counts.info > 0 ? "text-green" : undefined} />
          </div>
        )}

        {/* Filter tabs */}
        <div className="flex items-center gap-1 mb-6 bg-surface-2 rounded-xl p-1 w-fit">
          {FILTER_TABS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-body transition-colors",
                filter === key
                  ? "bg-surface border border-border text-text"
                  : "text-text-2 hover:text-text"
              )}
            >
              {label}
              {counts[key] > 0 && (
                <span className={cn(
                  "font-mono text-xs px-1.5 py-0.5 rounded-full",
                  filter === key ? "bg-surface-2 text-text-3" : "bg-surface border border-border text-text-3"
                )}>
                  {counts[key]}
                </span>
              )}
            </button>
          ))}
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <SkeletonCard key={i} className="h-20" />)}
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16">
            <EmptyState
              variant="no_alerts"
              title={filter === "all" ? "No active alerts" : `No ${filter} alerts`}
              description={filter === "all" ? "All properties are running normally." : "Try a different filter."}
            />
          </div>
        ) : (
          <div className="space-y-6">
            {(["critical", "warning", "info"] as AlertSeverity[]).map((sev) => {
              const items = filtered.filter((a) => a.severity === sev);
              if (!items.length) return null;
              const { label, icon: Icon, color } = SEVERITY_HEADER[sev];
              return (
                <div key={sev}>
                  {filter === "all" && (
                    <div className={cn("flex items-center gap-2 mb-3", color)}>
                      <Icon size={13} />
                      <span className="font-body font-normal text-xs uppercase tracking-widest">{label}</span>
                      <span className="font-mono text-xs ml-1 text-text-3">{items.length}</span>
                    </div>
                  )}
                  <div className="space-y-2">
                    <AnimatePresence mode="popLayout">
                      {items.map((alert, i) => (
                        <AlertCard
                          key={alert.id}
                          alert={alert}
                          onDismiss={() => dismiss.mutate(alert.id)}
                          index={i}
                        />
                      ))}
                    </AnimatePresence>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </motion.div>
    </PageWrapper>
  );
}
