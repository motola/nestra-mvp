"use client";

import { useQuery } from "@tanstack/react-query";
import { Building2, Cpu, Bell, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import { useProperties } from "@/hooks/useProperty";
import { useAlerts, useDismissAlert } from "@/hooks/useAlerts";
import { devicesApi } from "@/lib/api";
import type { AlphaconDevice } from "@/lib/types";
import {
  PageWrapper,
  StatCard,
  DonutChart,
  SkeletonCard,
  AlertCard,
} from "@/themes";
import { cn } from "@/lib/utils";

const DONUT_DATA = [
  { name: "Lights", value: 38, color: "#b17d3a" },
  { name: "Plugs", value: 27, color: "#9a5e15" },
  { name: "Sensors", value: 12, color: "#c4a166" },
  { name: "Locks", value: 5, color: "#e8dece" },
  { name: "Other", value: 18, color: "#d4c9b5" },
];

function getGreeting(): string {
  const h = new Date().getHours();
  if (h >= 5 && h < 12) return "Good morning";
  if (h >= 12 && h < 17) return "Good afternoon";
  if (h >= 17 && h < 22) return "Good evening";
  return "Good night";
}

export default function DashboardPage() {
  const { data: properties = [], isLoading: propsLoading } = useProperties();
  const { data: alerts = [], isLoading: alertsLoading } = useAlerts();
  const { data: devices = [] } = useQuery<AlphaconDevice[]>({
    queryKey: ["devices"],
    queryFn: devicesApi.list,
  });
  const dismiss = useDismissAlert();

  const activeAlerts = alerts.filter((a) => !a.dismissed);
  const criticalCount = activeAlerts.filter(
    (a) => a.severity === "critical",
  ).length;
  const warningCount = activeAlerts.filter(
    (a) => a.severity === "warning",
  ).length;

  const affectedProps = new Set(activeAlerts.map((a) => a.property_id)).size;
  const statusMsg =
    criticalCount > 0
      ? `Action required across ${affectedProps} propert${affectedProps !== 1 ? "ies" : "y"}.`
      : warningCount > 0
        ? `You have ${activeAlerts.length} item${activeAlerts.length !== 1 ? "s" : ""} to review.`
        : "Your portfolio is running normally.";

  return (
    <PageWrapper>
      <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-8">
        {/* Hero greeting */}
        <div className="mb-2">
          <h1 className="font-display italic text-[28px] text-text leading-tight">
            {getGreeting()}.
          </h1>
          <p className="font-body font-light text-[15px] text-text-3 mt-1">
            {statusMsg}
          </p>
        </div>

        {/* Critical alert banner */}
        {criticalCount > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-bg border border-red/20 rounded-xl px-4 py-3 flex items-center gap-3"
          >
            <Bell size={14} className="text-red flex-shrink-0" />
            <p className="font-body text-sm text-red">
              {criticalCount} critical alert{criticalCount !== 1 ? "s" : ""}{" "}
              require{criticalCount === 1 ? "s" : ""} attention
            </p>
            <a
              href="/alerts"
              className="ml-auto font-body font-light text-xs text-red hover:underline"
            >
              View alerts →
            </a>
          </motion.div>
        )}

        {/* Hero stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {propsLoading ? (
            [1, 2, 3, 4].map((i) => <SkeletonCard key={i} />)
          ) : (
            <>
              <StatCard
                label="Properties"
                value={properties.length}
                icon={Building2}
                animate
              />
              <StatCard
                label="Devices"
                value={devices.length || 47}
                icon={Cpu}
                animate
              />
              <StatCard
                label="Active Alerts"
                value={activeAlerts.length}
                icon={Bell}
                animate
                className={
                  activeAlerts.length > 0 ? "border-red/20 bg-red-bg" : ""
                }
              />
              <StatCard
                label="At Risk"
                value={affectedProps}
                icon={AlertTriangle}
                animate
                className={
                  affectedProps > 0 ? "border-amber/20 bg-amber-bg" : ""
                }
              />
            </>
          )}
        </div>

        {/* Device breakdown */}
        <div className="bg-surface border border-border rounded-xl p-5">
          <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-1">
            Device Types
          </p>
          <p className="font-display italic text-lg text-text mb-4">
            Breakdown
          </p>
          <DonutChart
            data={DONUT_DATA}
            total={devices.length || 47}
            label="devices"
            height={180}
          />
        </div>

        {/* Recent alerts */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3">
              Recent Alerts
            </p>
            <a
              href="/alerts"
              className="font-body font-light text-xs text-text-3 hover:text-text-2 transition-colors"
            >
              View all →
            </a>
          </div>
          {alertsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <SkeletonCard key={i} className="h-16" />
              ))}
            </div>
          ) : activeAlerts.length === 0 ? (
            <div className="bg-surface border border-border rounded-xl px-4 py-6 text-center">
              <p className="font-body font-light text-sm text-text-3">
                No active alerts — all systems normal
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {activeAlerts.slice(0, 5).map((alert, i) => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onDismiss={() => dismiss.mutate(alert.id)}
                  index={i}
                />
              ))}
            </div>
          )}
        </div>

        {/* Properties quick view */}
        {properties.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3">
                Your Properties
              </p>
              <a
                href="/portfolio"
                className="font-body font-light text-xs text-text-3 hover:text-text-2 transition-colors"
              >
                View all →
              </a>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {properties.slice(0, 3).map((p) => (
                <a
                  key={p.id}
                  href={`/properties/${p.id}`}
                  className="bg-surface border border-border rounded-xl p-4 hover:border-border-strong hover:shadow-sm transition-all group"
                >
                  <div className="flex items-start justify-between mb-2">
                    <p className="font-display italic text-sm text-text group-hover:text-graphite transition-colors">
                      {p.name}
                    </p>
                    <span
                      className={cn(
                        "w-2 h-2 rounded-full flex-shrink-0 mt-1",
                        p.status === "critical"
                          ? "bg-red"
                          : p.status === "needs_attention"
                            ? "bg-amber"
                            : "bg-green",
                      )}
                    />
                  </div>
                  <p className="font-mono text-xs text-text-3 truncate">
                    {p.address}
                  </p>
                  <div className="flex items-center gap-3 mt-3">
                    <span className="font-mono text-xs text-text-3">
                      {p.device_count} devices
                    </span>
                    {p.alert_count > 0 && (
                      <span className="font-mono text-xs text-red">
                        {p.alert_count} alert{p.alert_count !== 1 ? "s" : ""}
                      </span>
                    )}
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </PageWrapper>
  );
}
