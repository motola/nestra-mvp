"use client";

import { useState } from "react";
import { TrendingDown, Zap, BarChart2, Leaf } from "lucide-react";
import { format, subDays } from "date-fns";
import { useProperties } from "@/hooks/useProperty";
import { PageWrapper, StatCard, EnergyChart, DonutChart, SkeletonCard } from "@/themes";
import { cn } from "@/lib/utils";

type Period = "today" | "7d" | "30d";

function seededEnergy(days: number, seed = 77): { label: string; value: number }[] {
  let s = seed;
  const lcg = () => { s = (s * 1664525 + 1013904223) & 0xffffffff; return (s >>> 0) / 4294967296; };
  if (days === 1) {
    return Array.from({ length: 24 }, (_, i) => ({
      label: `${String(i).padStart(2, "0")}:00`,
      value: 0.8 + lcg() * 1.4,
    }));
  }
  return Array.from({ length: days }, (_, i) => {
    const d = subDays(new Date(), days - 1 - i);
    return { label: format(d, days <= 7 ? "EEE" : "d MMM"), value: 18 + lcg() * 14 };
  });
}

const PROPERTY_BREAKDOWN = [
  { name: "Mayfair House", value: 42, color: "#9a5e15" },
  { name: "Camden Flat", value: 28, color: "#b17d3a" },
  { name: "Shoreditch Loft", value: 19, color: "#c4a166" },
  { name: "Others", value: 11, color: "#d4c9b5" },
];

const PERIOD_STATS: Record<Period, { total: string; cost: string; change: string; positive: boolean }> = {
  today: { total: "22.4", cost: "£4.83", change: "-3.1%", positive: true },
  "7d": { total: "214.7", cost: "£46.31", change: "-8.2%", positive: true },
  "30d": { total: "891.2", cost: "£192.16", change: "+2.4%", positive: false },
};

export default function EnergyPage() {
  const { data: properties = [], isLoading } = useProperties();
  const [period, setPeriod] = useState<Period>("7d");

  const chartDays = period === "today" ? 1 : period === "7d" ? 7 : 30;
  const energyData = seededEnergy(chartDays);
  const stats = PERIOD_STATS[period];

  return (
    <PageWrapper>
      <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-display italic text-2xl text-text">Energy</h1>
            <p className="font-body font-light text-sm text-text-3 mt-1">Portfolio energy consumption analytics</p>
          </div>
          {/* Period toggle */}
          <div className="flex items-center gap-1 bg-surface-2 border border-border rounded-lg p-1">
            {(["today", "7d", "30d"] as Period[]).map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={cn(
                  "px-3 py-1.5 rounded-md text-xs font-body font-light transition-colors",
                  period === p ? "bg-surface text-text shadow-sm" : "text-text-3 hover:text-text-2"
                )}
              >
                {p === "today" ? "Today" : p === "7d" ? "7 days" : "30 days"}
              </button>
            ))}
          </div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Consumed" value={stats.total} unit="kWh" icon={Zap} animate />
          <StatCard label="Estimated Cost" value={stats.cost} icon={BarChart2} />
          <StatCard
            label="vs Prior Period"
            value={stats.change}
            icon={TrendingDown}
            className={stats.positive ? "border-green/20" : "border-red/20"}
          />
          <StatCard label="CO₂ Saved" value="18.3" unit="kg" icon={Leaf} animate />
        </div>

        {/* Main chart */}
        <div className="bg-surface border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3">Consumption</p>
              <p className="font-display italic text-lg text-text mt-0.5">
                {period === "today" ? "Today by hour" : period === "7d" ? "Past 7 days" : "Past 30 days"}
              </p>
            </div>
          </div>
          <EnergyChart data={energyData} height={220} />
        </div>

        {/* Split: property breakdown + per-property table */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-surface border border-border rounded-xl p-5">
            <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-1">By Property</p>
            <p className="font-display italic text-lg text-text mb-4">Share</p>
            <DonutChart data={PROPERTY_BREAKDOWN} total={100} label="%" height={160} />
          </div>

          <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-5">
            <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-4">Property Breakdown</p>
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => <SkeletonCard key={i} className="h-10" />)}
              </div>
            ) : (
              <div className="space-y-3">
                {(properties.length > 0 ? properties : [
                  { id: "1", name: "Mayfair House", address: "12 Mayfair Rd", kwh: "42.0", cost: "£9.07", change: "-5%" },
                  { id: "2", name: "Camden Flat", address: "7 Camden Ave", kwh: "28.0", cost: "£6.04", change: "-2%" },
                  { id: "3", name: "Shoreditch Loft", address: "22 Brick Ln", kwh: "19.0", cost: "£4.10", change: "+1%" },
                ] as { id: string; name: string; address: string; kwh?: string | number; cost?: string; change?: string }[]).map((p, i) => {
                  const share = PROPERTY_BREAKDOWN[i] ?? { value: 5 };
                  return (
                    <div key={p.id} className="flex items-center gap-3">
                      <div
                        className="w-2 h-2 rounded-full flex-shrink-0"
                        style={{ background: PROPERTY_BREAKDOWN[i]?.color ?? "#d4c9b5" }}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="font-body text-sm text-text truncate">{p.name}</p>
                          <p className="font-mono text-xs text-text-3 ml-2 flex-shrink-0">{share.value}%</p>
                        </div>
                        <div className="mt-1 h-1 bg-surface-2 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{ width: `${share.value}%`, background: PROPERTY_BREAKDOWN[i]?.color ?? "#d4c9b5" }}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </PageWrapper>
  );
}
