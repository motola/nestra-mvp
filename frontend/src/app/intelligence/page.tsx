"use client";

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Brain, CheckCircle, MapPin, XCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { format } from "date-fns";
import { intelligenceApi } from "@/lib/api";
import type { IntelligenceItem, IntelligenceSeverity } from "@/lib/types";
import { cn } from "@/lib/utils";
import { PageWrapper, SkeletonCard, EmptyState } from "@/themes";

type Filter = "all" | IntelligenceSeverity;

const SEV_ICON: Record<IntelligenceSeverity, typeof CheckCircle> = {
  critical: XCircle,
  warning: AlertTriangle,
  info: CheckCircle,
};
const SEV_COLOR: Record<IntelligenceSeverity, string> = {
  critical: "text-red",
  warning: "text-amber",
  info: "text-green",
};
const SEV_DOT: Record<IntelligenceSeverity, string> = {
  critical: "bg-red",
  warning: "bg-amber",
  info: "bg-green",
};
const CARD_BG: Record<IntelligenceSeverity, string> = {
  critical: "bg-red-bg border-red/20 border-l-red",
  warning: "bg-amber-bg border-amber/20 border-l-amber",
  info: "border-border border-l-border",
};

function worstSeverity(items: IntelligenceItem[]): IntelligenceSeverity | null {
  if (items.some((i) => i.severity === "critical")) return "critical";
  if (items.some((i) => i.severity === "warning")) return "warning";
  if (items.some((i) => i.severity === "info")) return "info";
  return null;
}

function HeroSummary({ items }: { items: IntelligenceItem[] }) {
  const worst = worstSeverity(items);
  const critCount = items.filter((i) => i.severity === "critical").length;
  const warnCount = items.filter((i) => i.severity === "warning").length;

  if (items.length === 0) return null;

  const { bg, border, text, icon: Icon, headline, sub } = (() => {
    if (worst === "critical") return {
      bg: "bg-red-bg", border: "border-red/20", text: "text-red", icon: XCircle,
      headline: `${critCount} critical issue${critCount !== 1 ? "s" : ""} need${critCount === 1 ? "s" : ""} attention`,
      sub: "Review and resolve critical alerts before they cause equipment damage or tenant disruption.",
    };
    if (worst === "warning") return {
      bg: "bg-amber-bg", border: "border-amber/20", text: "text-amber", icon: AlertTriangle,
      headline: `${warnCount} warning${warnCount !== 1 ? "s" : ""} detected across your portfolio`,
      sub: "These issues are non-urgent but should be addressed this week.",
    };
    return {
      bg: "bg-green-bg", border: "border-green/20", text: "text-green", icon: CheckCircle,
      headline: "Portfolio looks healthy",
      sub: `${items.length} informational insight${items.length !== 1 ? "s" : ""} available for review.`,
    };
  })();

  return (
    <motion.div
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn("border rounded-xl p-5 flex items-start gap-3 mb-6", bg, border)}
    >
      <Icon size={20} className={cn("flex-shrink-0 mt-0.5", text)} />
      <div>
        <p className={cn("font-body font-normal text-[15px]", text)}>{headline}</p>
        <p className="font-body font-light text-[13px] text-text-2 mt-0.5">{sub}</p>
      </div>
    </motion.div>
  );
}

function InsightCardFull({ item, index }: { item: IntelligenceItem; index: number }) {
  const sev = item.severity;
  const Icon = SEV_ICON[sev];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2, delay: index * 0.04 }}
      className={cn(
        "border border-l-4 rounded-r-xl p-4 bg-surface",
        CARD_BG[sev]
      )}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={cn("flex items-center gap-1 font-mono text-[11px] px-2 py-0.5 rounded-full border", {
            "bg-red-bg text-red border-red/20": sev === "critical",
            "bg-amber-bg text-amber border-amber/20": sev === "warning",
            "bg-green-bg text-green border-green/20": sev === "info",
          })}>
            <Icon size={9} />
            {sev.charAt(0).toUpperCase() + sev.slice(1)}
          </span>
          <span className="font-mono text-[11px] px-2 py-0.5 rounded-full bg-surface-2 border border-border text-text-3">
            {item.type.replace(/_/g, " ")}
          </span>
        </div>
        {item.metric != null && (
          <span className={cn("font-mono text-lg font-medium flex-shrink-0", SEV_COLOR[sev])}>
            {item.metric % 1 === 0 ? item.metric : item.metric.toFixed(1)}
            {item.unit && <span className="text-xs font-normal text-text-3 ml-0.5">{item.unit}</span>}
          </span>
        )}
      </div>

      <p className="font-body font-normal text-[15px] text-text mb-1.5">{item.title}</p>
      <p className="font-body font-light text-[13px] text-text-2 leading-relaxed mb-3">{item.detail}</p>

      <div className="flex items-center justify-between">
        <a
          href={`/properties/${item.property_id}`}
          className="flex items-center gap-1 font-mono text-[11px] text-text-3 hover:text-text-2 transition-colors"
        >
          <MapPin size={10} />
          {item.property_name}
        </a>
        <p className="font-mono text-[11px] text-text-3">
          {format(new Date(item.generated_at), "d MMM, HH:mm")}
        </p>
      </div>
    </motion.div>
  );
}

export default function IntelligencePage() {
  const { data: items = [], isLoading } = useQuery<IntelligenceItem[]>({
    queryKey: ["intelligence"],
    queryFn: intelligenceApi.list,
    staleTime: 5 * 60 * 1000,
  });

  const [selectedProperty, setSelectedProperty] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("all");

  const properties = useMemo(() => {
    const map = new Map<string, { id: string; name: string; items: IntelligenceItem[] }>();
    items.forEach((item) => {
      if (!map.has(item.property_id)) {
        map.set(item.property_id, { id: item.property_id, name: item.property_name, items: [] });
      }
      map.get(item.property_id)!.items.push(item);
    });
    return Array.from(map.values());
  }, [items]);

  const baseItems = selectedProperty ? items.filter((i) => i.property_id === selectedProperty) : items;

  const filtered = useMemo(() => {
    return filter !== "all" ? baseItems.filter((i) => i.severity === filter) : baseItems;
  }, [baseItems, filter]);

  const counts: Record<Filter, number> = {
    all: baseItems.length,
    critical: baseItems.filter((i) => i.severity === "critical").length,
    warning: baseItems.filter((i) => i.severity === "warning").length,
    info: baseItems.filter((i) => i.severity === "info").length,
  };

  return (
    <PageWrapper>
      <div className="flex h-full" style={{ height: "calc(100vh - 52px)" }}>
        {/* Left pane — property filter */}
        <aside className="hidden md:flex w-[260px] flex-shrink-0 bg-surface-2 border-r border-border flex-col">
          <div className="px-4 py-4 border-b border-border">
            <p className="font-mono text-[10px] text-text-3 uppercase tracking-widest">Properties</p>
          </div>
          <nav className="flex-1 overflow-y-auto py-2">
            <button
              onClick={() => setSelectedProperty(null)}
              className={cn(
                "w-full flex items-center gap-2.5 px-4 py-2.5 text-left transition-colors",
                selectedProperty === null
                  ? "bg-surface border-l-2 border-l-graphite text-text"
                  : "text-text-2 hover:bg-surface hover:text-text"
              )}
            >
              <span className="w-2 h-2 rounded-full bg-text-3 flex-shrink-0" />
              <span className="font-body font-light text-sm flex-1">All Properties</span>
              <span className="font-mono text-xs text-text-3">{items.length}</span>
            </button>

            {properties.map((prop) => {
              const worst = worstSeverity(prop.items);
              return (
                <button
                  key={prop.id}
                  onClick={() => setSelectedProperty(prop.id)}
                  className={cn(
                    "w-full flex items-center gap-2.5 px-4 py-2.5 text-left transition-colors",
                    selectedProperty === prop.id
                      ? "bg-surface border-l-2 border-l-graphite text-text"
                      : "text-text-2 hover:bg-surface hover:text-text"
                  )}
                >
                  {worst ? (
                    <span className={cn("w-2 h-2 rounded-full flex-shrink-0", SEV_DOT[worst])} />
                  ) : (
                    <span className="w-2 h-2 rounded-full bg-text-3 flex-shrink-0" />
                  )}
                  <span className="font-body font-light text-sm flex-1 truncate">{prop.name}</span>
                  <span className="font-mono text-xs text-text-3">{prop.items.length}</span>
                </button>
              );
            })}
          </nav>
        </aside>

        {/* Right pane */}
        <div className="flex-1 overflow-y-auto bg-bg">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="p-6 md:p-8 max-w-3xl"
          >
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-1">
                <Brain size={18} className="text-text-2" />
                <h1 className="font-display italic text-[28px] text-text leading-tight">Intelligence</h1>
              </div>
              <p className="font-body font-light text-[14px] text-text-3">
                AI analysis across your portfolio
              </p>
            </div>

            {/* Hero summary */}
            {!isLoading && items.length > 0 && <HeroSummary items={baseItems} />}

            {/* Filter chips */}
            <div className="flex items-center gap-2 mb-6 flex-wrap">
              {(["all", "critical", "warning", "info"] as Filter[]).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-body font-light transition-colors",
                    filter === f
                      ? "bg-graphite text-surface"
                      : "bg-surface border border-border text-text-3 hover:text-text hover:border-border-strong"
                  )}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                  {counts[f] > 0 && (
                    <span className="font-mono">{counts[f]}</span>
                  )}
                </button>
              ))}
            </div>

            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => <SkeletonCard key={i} className="h-28" />)}
              </div>
            ) : filtered.length === 0 ? (
              <div className="py-16">
                <EmptyState
                  variant="no_insights"
                  title="No intelligence data"
                  description={
                    filter !== "all"
                      ? `No ${filter} insights for this selection.`
                      : "Enable demo mode or connect properties to generate AI insights."
                  }
                />
              </div>
            ) : (
              <div className="space-y-3">
                <AnimatePresence mode="popLayout">
                  {filtered.map((item, i) => (
                    <InsightCardFull key={item.id} item={item} index={i} />
                  ))}
                </AnimatePresence>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </PageWrapper>
  );
}
