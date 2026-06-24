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
  TrendChart,
  SkeletonCard,
  AlertCard,
} from "@/themes";
import { cn } from "@/lib/utils";

const DEVICE_TYPE_DATA = [
  { name: "Lights", value: 38, color: "#b17d3a" },
  { name: "Plugs", value: 27, color: "#9a5e15" },
  { name: "Sensors", value: 12, color: "#c4a166" },
  { name: "Locks", value: 5, color: "#e8dece" },
  { name: "Other", value: 18, color: "#d4c9b5" },
];

function seededSeries(
  seed: string,
  days: number,
  base: number,
  range: number,
): { label: string; value: number }[] {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  return Array.from({ length: days }, (_, i) => {
    h = (h * 1664525 + 1013904223) >>> 0;
    const d = new Date();
    d.setDate(d.getDate() - (days - 1 - i));
    return {
      label: `${d.getDate()}/${d.getMonth() + 1}`,
      value: Math.round(base + ((h % 1000) / 1000) * range),
    };
  });
}

function getGreeting(): string {
  const h = new Date().getHours();
  if (h >= 5 && h < 12) return "Good morning";
  if (h >= 12 && h < 17) return "Good afternoon";
  if (h >= 17 && h < 22) return "Good evening";
  return "Good night";
}

function ChartCard({
  label,
  title,
  children,
  className,
}: {
  label: string;
  title: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "bg-surface border border-border rounded-xl p-5",
        className,
      )}
    >
      <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3">
        {label}
      </p>
      <p className="font-display italic text-lg text-text mt-0.5 mb-4">
        {title}
      </p>
      {children}
    </div>
  );
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
  const infoCount = activeAlerts.filter((a) => a.severity === "info").length;

  const deviceCount = devices.length || 31;
  const onlineCount = devices.length
    ? devices.filter((d) => d.online).length
    : 27;
  const offlineCount = Math.max(deviceCount - onlineCount, 0);

  const affectedProps = new Set(activeAlerts.map((a) => a.property_id)).size;
  const healthy = properties.filter((p) => p.status === "all_clear").length;
  const needs = properties.filter((p) => p.status === "needs_attention").length;
  const critical = properties.filter((p) => p.status === "critical").length;

  const activityData = seededSeries("portfolio-activity", 14, 40, 80);
  const severityData = [
    { name: "Critical", value: criticalCount, color: "#9a2828" },
    { name: "Warning", value: warningCount, color: "#9a5e15" },
    { name: "Info", value: infoCount, color: "#2d6b2d" },
  ].filter((s) => s.value > 0);
  const statusData = [
    { name: "Online", value: onlineCount, color: "#2d6b2d" },
    { name: "Offline", value: offlineCount, color: "#a39d8e" },
  ];

  const statusBars = [
    { label: "Healthy", count: healthy, color: "bg-green" },
    { label: "Needs attention", count: needs, color: "bg-amber" },
    { label: "Critical", count: critical, color: "bg-red" },
  ];

  const statusMsg =
    criticalCount > 0
      ? `Action required across ${affectedProps} propert${affectedProps !== 1 ? "ies" : "y"}.`
      : warningCount > 0
        ? `You have ${activeAlerts.length} item${activeAlerts.length !== 1 ? "s" : ""} to review.`
        : "Your portfolio is running normally.";

  return (
    <PageWrapper>
      <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-6">
        {/* Hero greeting */}
        <div>
          <h1 className="font-display italic text-[28px] text-text leading-tight">
            {getGreeting()}.
          </h1>
          <p className="font-body font-light text-[15px] text-text-3 mt-1">
            {statusMsg}
          </p>
        </div>

        {/* Critical banner */}
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

        {/* Hero stats with sparklines */}
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
                trend="properties-trend"
                sub="all monitored"
              />
              <StatCard
                label="Devices"
                value={deviceCount}
                icon={Cpu}
                animate
                trend="devices-trend"
                sub={`${onlineCount} online`}
              />
              <StatCard
                label="Active alerts"
                value={activeAlerts.length}
                icon={Bell}
                animate
                trend="alerts-trend"
                sub={`${criticalCount} critical`}
                className={
                  activeAlerts.length > 0 ? "border-amber/20 bg-amber-bg" : ""
                }
              />
              <StatCard
                label="At risk"
                value={affectedProps}
                icon={AlertTriangle}
                animate
                trend="risk-trend"
                sub="properties"
                className={affectedProps > 0 ? "border-red/20 bg-red-bg" : ""}
              />
            </>
          )}
        </div>

        {/* Analytics row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <ChartCard
            label="Portfolio activity"
            title="Device events · last 14 days"
            className="lg:col-span-2"
          >
            <TrendChart data={activityData} height={210} />
          </ChartCard>
          <ChartCard label="Alerts" title="By severity">
            {severityData.length > 0 ? (
              <DonutChart
                data={severityData}
                total={activeAlerts.length}
                label="alerts"
                height={210}
              />
            ) : (
              <div className="h-[210px] flex items-center justify-center font-body font-light text-sm text-text-3">
                No active alerts
              </div>
            )}
          </ChartCard>
        </div>

        {/* Analytics row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <ChartCard label="Devices" title="Online status">
            <DonutChart
              data={statusData}
              total={deviceCount}
              label="devices"
              height={200}
            />
          </ChartCard>
          <ChartCard label="Devices" title="By type">
            <DonutChart
              data={DEVICE_TYPE_DATA}
              total={deviceCount}
              label="devices"
              height={200}
            />
          </ChartCard>
          <ChartCard label="Portfolio" title="Property health">
            <div className="space-y-4 pt-2">
              {statusBars.map((row) => (
                <div key={row.label}>
                  <div className="flex justify-between items-baseline mb-1.5">
                    <span className="font-body font-light text-sm text-text-2">
                      {row.label}
                    </span>
                    <span className="font-mono text-sm text-text tabular-nums">
                      {row.count}
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-surface-2 overflow-hidden">
                    <div
                      className={cn("h-full rounded-full", row.color)}
                      style={{
                        width: `${(row.count / (properties.length || 1)) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </ChartCard>
        </div>

        {/* Recent alerts */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3">
              Recent alerts
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
                Your properties
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
                  className="bg-surface border border-border rounded-xl p-4 hover:border-border-strong transition-all group"
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
