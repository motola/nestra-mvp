"use client";

import { useState } from "react";
import { Building2, LayoutGrid, List } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useProperties } from "@/hooks/useProperty";
import { PageWrapper, PropertyCard, SkeletonCard, EmptyState } from "@/themes";
import { cn } from "@/lib/utils";
import type { PropertyStatus } from "@/lib/types";

const STATUS_FILTERS: { label: string; value: PropertyStatus | "all" }[] = [
  { label: "All", value: "all" },
  { label: "All Clear", value: "all_clear" },
  { label: "Needs Attention", value: "needs_attention" },
  { label: "Critical", value: "critical" },
];

export default function PortfolioPage() {
  const { data: properties = [], isLoading, isError } = useProperties();
  const [view, setView] = useState<"grid" | "list">("grid");
  const [filter, setFilter] = useState<PropertyStatus | "all">("all");

  const filtered = filter === "all" ? properties : properties.filter((p) => p.status === filter);

  return (
    <PageWrapper>
      <div className="p-6 md:p-8 max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="font-display italic text-2xl text-text">Portfolio</h1>
            <p className="font-body font-light text-sm text-text-3 mt-1">
              {isLoading ? "Loading…" : `${properties.length} propert${properties.length !== 1 ? "ies" : "y"}`}
            </p>
          </div>
          {/* View toggle */}
          <div className="flex items-center gap-1 bg-surface-2 border border-border rounded-lg p-1">
            <button
              onClick={() => setView("grid")}
              className={cn(
                "p-1.5 rounded-md transition-colors",
                view === "grid" ? "bg-surface text-text shadow-sm" : "text-text-3 hover:text-text-2"
              )}
            >
              <LayoutGrid size={14} />
            </button>
            <button
              onClick={() => setView("list")}
              className={cn(
                "p-1.5 rounded-md transition-colors",
                view === "list" ? "bg-surface text-text shadow-sm" : "text-text-3 hover:text-text-2"
              )}
            >
              <List size={14} />
            </button>
          </div>
        </div>

        {/* Filter chips */}
        <div className="flex items-center gap-2 mb-6 flex-wrap">
          {STATUS_FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className={cn(
                "px-3 py-1.5 rounded-full text-xs font-body font-light transition-colors",
                filter === f.value
                  ? "bg-graphite text-surface"
                  : "bg-surface border border-border text-text-3 hover:text-text hover:border-border-strong"
              )}
            >
              {f.label}
              {f.value !== "all" && (
                <span className="ml-1.5 opacity-60">
                  {properties.filter((p) => p.status === f.value).length}
                </span>
              )}
            </button>
          ))}
        </div>

        {isError && (
          <div className="bg-red-bg border border-red/20 rounded-xl p-4 text-sm text-red mb-6">
            Could not load properties. Make sure the backend is running on port 8000.
          </div>
        )}

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => <SkeletonCard key={i} />)}
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16">
            <EmptyState
              icon={Building2}
              title={filter === "all" ? "No properties yet" : `No ${filter.replace("_", " ")} properties`}
              description={filter === "all" ? "Add your first property to start monitoring it." : "Try changing the filter."}
            />
          </div>
        ) : view === "grid" ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <AnimatePresence mode="popLayout">
              {filtered.map((property, i) => (
                <PropertyCard key={property.id} property={property} index={i} />
              ))}
            </AnimatePresence>
          </div>
        ) : (
          <div className="space-y-2">
            <AnimatePresence mode="popLayout">
              {filtered.map((property, i) => (
                <motion.a
                  key={property.id}
                  href={`/properties/${property.id}`}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -8 }}
                  transition={{ delay: i * 0.03 }}
                  className="flex items-center gap-4 bg-surface border border-border rounded-xl px-5 py-4 hover:border-border-strong transition-colors group"
                >
                  <span className={cn(
                    "w-2.5 h-2.5 rounded-full flex-shrink-0",
                    property.status === "critical" ? "bg-red" :
                    property.status === "needs_attention" ? "bg-amber" : "bg-green"
                  )} />
                  <div className="flex-1 min-w-0">
                    <p className="font-display italic text-sm text-text group-hover:text-graphite transition-colors">{property.name}</p>
                    <p className="font-mono text-xs text-text-3 truncate mt-0.5">{property.address}</p>
                  </div>
                  <div className="flex items-center gap-4 flex-shrink-0">
                    <span className="font-mono text-xs text-text-3 hidden sm:block">{property.device_count} devices</span>
                    {property.alert_count > 0 && (
                      <span className="font-mono text-xs text-red">{property.alert_count} alert{property.alert_count !== 1 ? "s" : ""}</span>
                    )}
                    {property.is_demo && (
                      <span className="font-mono text-[10px] bg-surface-2 border border-border text-text-3 px-1.5 py-0.5 rounded-full">Demo</span>
                    )}
                  </div>
                </motion.a>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </PageWrapper>
  );
}
