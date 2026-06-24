"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import {
  Building2,
  Cpu,
  Bell,
  AlertTriangle,
  XCircle,
  CheckCircle,
  ChevronRight,
} from "lucide-react";
import { motion } from "framer-motion";
import { format } from "date-fns";
import { useProperties } from "@/hooks/useProperty";
import { useAlerts } from "@/hooks/useAlerts";
import { devicesApi } from "@/lib/api";
import type {
  AlphaconDevice,
  PropertyStatus,
  AlertSeverity,
} from "@/lib/types";
import { PageWrapper, StatCard, TrendChart, SkeletonCard } from "@/themes";
import { cn } from "@/lib/utils";

const STATUS_RANK: Record<PropertyStatus, number> = {
  critical: 2,
  needs_attention: 1,
  all_clear: 0,
};
const STATUS_META: Record<PropertyStatus, { label: string; cls: string }> = {
  critical: { label: "Critical", cls: "bg-red-bg text-red border-red/20" },
  needs_attention: {
    label: "Needs attention",
    cls: "bg-amber-bg text-amber border-amber/20",
  },
  all_clear: {
    label: "All clear",
    cls: "bg-green-bg text-green border-green/20",
  },
};
const SEV_RANK: Record<AlertSeverity, number> = {
  critical: 2,
  warning: 1,
  info: 0,
};

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
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.4, ease: [0.2, 0.8, 0.2, 1] }}
      className={cn(
        "bg-surface border border-border rounded-xl p-5 elevate elevate-hover",
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
    </motion.div>
  );
}

export default function DashboardPage() {
  const { data: properties = [], isLoading: propsLoading } = useProperties();
  const { data: alerts = [], isLoading: alertsLoading } = useAlerts();
  const { data: devices = [] } = useQuery<AlphaconDevice[]>({
    queryKey: ["devices"],
    queryFn: devicesApi.list,
  });
  const router = useRouter();

  const activeAlerts = alerts.filter((a) => !a.dismissed);
  const criticalCount = activeAlerts.filter(
    (a) => a.severity === "critical",
  ).length;
  const warningCount = activeAlerts.filter(
    (a) => a.severity === "warning",
  ).length;

  const deviceCount = devices.length;
  const onlineCount = devices.filter((d) => d.online).length;
  const affectedProps = new Set(activeAlerts.map((a) => a.property_id)).size;

  const activityData = devices.length
    ? seededSeries("portfolio-activity", 14, 40, 80)
    : [];

  const sortedProperties = [...properties].sort(
    (a, b) => STATUS_RANK[b.status] - STATUS_RANK[a.status],
  );
  const prioritized = [...activeAlerts].sort(
    (a, b) => SEV_RANK[b.severity] - SEV_RANK[a.severity],
  );

  const statusMsg =
    criticalCount > 0
      ? `Action required across ${affectedProps} propert${affectedProps !== 1 ? "ies" : "y"}.`
      : warningCount > 0
        ? `You have ${activeAlerts.length} item${activeAlerts.length !== 1 ? "s" : ""} to review.`
        : "Your portfolio is running normally.";

  return (
    <PageWrapper>
      <div className="p-6 md:p-8 max-w-[1600px] mx-auto space-y-6">
        {/* Hero jumbotron */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.2, 0.8, 0.2, 1] }}
          className="relative overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-surface to-surface-2 px-6 py-7 md:px-8 md:py-8 elevate"
        >
          <div className="pointer-events-none absolute -top-16 -right-12 w-64 h-64 rounded-full bg-accent/5 blur-3xl" />
          <p className="font-mono text-[11px] uppercase tracking-widest text-text-3 mb-2">
            {new Date().toLocaleDateString(undefined, {
              weekday: "long",
              day: "numeric",
              month: "long",
            })}
          </p>
          <h1 className="font-display italic text-[32px] md:text-[36px] text-text leading-[1.05]">
            {getGreeting()}.
          </h1>
          <p className="font-body font-light text-[15px] text-text-2 mt-2 max-w-lg">
            {statusMsg}
          </p>
        </motion.div>

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
                sub="all monitored"
              />
              <StatCard
                label="Devices"
                value={deviceCount}
                icon={Cpu}
                animate
                sub={`${onlineCount} online`}
              />
              <StatCard
                label="Active alerts"
                value={activeAlerts.length}
                icon={Bell}
                animate
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
                sub="properties"
                className={affectedProps > 0 ? "border-red/20 bg-red-bg" : ""}
              />
            </>
          )}
        </div>

        {/* Portfolio activity trend */}
        <ChartCard
          label="Portfolio activity"
          title="Device events · last 14 days"
        >
          <TrendChart data={activityData} height={170} />
        </ChartCard>

        {/* Property health table + priority issues */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Dominant property-health table */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.4, ease: [0.2, 0.8, 0.2, 1] }}
            className="lg:col-span-2 bg-surface border border-border rounded-xl elevate overflow-hidden"
          >
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-border">
              <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3">
                Property health
              </p>
              <a
                href="/portfolio"
                className="font-body font-light text-xs text-text-3 hover:text-text-2 transition-colors"
              >
                View all →
              </a>
            </div>
            {propsLoading ? (
              <div className="p-5 space-y-3">
                {[1, 2, 3, 4].map((i) => (
                  <SkeletonCard key={i} className="h-10" />
                ))}
              </div>
            ) : sortedProperties.length === 0 ? (
              <div className="px-5 py-10 text-center font-body font-light text-sm text-text-3">
                No properties yet.
              </div>
            ) : (
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="font-body font-normal text-[11px] uppercase tracking-wider text-text-3 text-left px-5 py-2.5">
                      Status
                    </th>
                    <th className="font-body font-normal text-[11px] uppercase tracking-wider text-text-3 text-left px-2 py-2.5">
                      Property
                    </th>
                    <th className="font-body font-normal text-[11px] uppercase tracking-wider text-text-3 text-right px-2 py-2.5">
                      Devices
                    </th>
                    <th className="font-body font-normal text-[11px] uppercase tracking-wider text-text-3 text-right px-5 py-2.5">
                      Alerts
                    </th>
                    <th className="w-8" />
                  </tr>
                </thead>
                <tbody>
                  {sortedProperties.map((p) => (
                    <tr
                      key={p.id}
                      onClick={() => router.push(`/properties/${p.id}`)}
                      className="border-t border-border hover:bg-surface-2 transition-colors cursor-pointer group"
                    >
                      <td className="px-5 py-3">
                        <span
                          className={cn(
                            "inline-flex items-center font-mono text-[11px] px-2 py-0.5 rounded-full border whitespace-nowrap",
                            STATUS_META[p.status].cls,
                          )}
                        >
                          {STATUS_META[p.status].label}
                        </span>
                      </td>
                      <td className="px-2 py-3 max-w-0">
                        <p className="font-body text-sm text-text truncate">
                          {p.name}
                        </p>
                        <p className="font-mono text-[11px] text-text-3 truncate">
                          {p.address.split(",").slice(-2).join(",").trim()}
                        </p>
                      </td>
                      <td className="px-2 py-3 text-right font-mono text-sm text-text-2 tabular-nums">
                        {p.device_count}
                      </td>
                      <td className="px-5 py-3 text-right font-mono text-sm tabular-nums">
                        {p.alert_count > 0 ? (
                          <span className="text-amber">{p.alert_count}</span>
                        ) : (
                          <span className="text-text-3">—</span>
                        )}
                      </td>
                      <td className="pr-4 text-text-3">
                        <ChevronRight
                          size={14}
                          className="opacity-0 group-hover:opacity-100 transition-opacity"
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </motion.div>

          {/* Priority issues */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.4, ease: [0.2, 0.8, 0.2, 1] }}
            className="bg-surface border border-border rounded-xl elevate overflow-hidden flex flex-col"
          >
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-border">
              <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3">
                Priority issues
              </p>
              <a
                href="/alerts"
                className="font-body font-light text-xs text-text-3 hover:text-text-2 transition-colors"
              >
                All →
              </a>
            </div>
            {alertsLoading ? (
              <div className="p-5 space-y-3">
                {[1, 2, 3].map((i) => (
                  <SkeletonCard key={i} className="h-12" />
                ))}
              </div>
            ) : prioritized.length === 0 ? (
              <div className="flex-1 flex items-center justify-center px-5 py-12 text-center">
                <div>
                  <CheckCircle
                    size={22}
                    className="text-green mx-auto mb-2 opacity-70"
                  />
                  <p className="font-body font-light text-sm text-text-3">
                    No active issues
                  </p>
                </div>
              </div>
            ) : (
              <div className="divide-y divide-border">
                {prioritized.slice(0, 6).map((a) => (
                  <a
                    key={a.id}
                    href={`/properties/${a.property_id}/devices/${a.device_id}`}
                    className="flex items-start gap-2.5 px-5 py-3 hover:bg-surface-2 transition-colors"
                  >
                    {a.severity === "critical" ? (
                      <XCircle
                        size={15}
                        className="text-red flex-shrink-0 mt-0.5"
                      />
                    ) : a.severity === "warning" ? (
                      <AlertTriangle
                        size={15}
                        className="text-amber flex-shrink-0 mt-0.5"
                      />
                    ) : (
                      <Bell
                        size={15}
                        className="text-text-3 flex-shrink-0 mt-0.5"
                      />
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="font-body text-[13px] text-text leading-snug line-clamp-2">
                        {a.message}
                      </p>
                      <p className="font-mono text-[11px] text-text-3 mt-0.5 truncate">
                        {a.device_name} ·{" "}
                        {format(new Date(a.created_at), "d MMM, HH:mm")}
                      </p>
                    </div>
                  </a>
                ))}
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </PageWrapper>
  );
}
