"use client";

import {
  Activity,
  AlertTriangle,
  Brain,
  CheckCircle,
  Droplets,
  Gauge,
  MapPin,
  Shield,
  XCircle,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";
import type {
  IntelligenceItem,
  IntelligenceSeverity,
  IntelligenceType,
} from "@/lib/types";
import { cn } from "@/lib/utils";

const SEVERITY: Record<
  IntelligenceSeverity,
  {
    border: string;
    bg: string;
    text: string;
    badge: string;
    icon: typeof CheckCircle;
  }
> = {
  critical: {
    border: "border-l-red",
    bg: "bg-red-bg",
    text: "text-red",
    badge: "bg-red-bg text-red border-red/20",
    icon: XCircle,
  },
  warning: {
    border: "border-l-amber",
    bg: "bg-amber-bg",
    text: "text-amber",
    badge: "bg-amber-bg text-amber border-amber/20",
    icon: AlertTriangle,
  },
  info: {
    border: "border-l-green",
    bg: "",
    text: "text-green",
    badge: "bg-green-bg text-green border-green/20",
    icon: CheckCircle,
  },
};

const TYPE_CONFIG: Record<
  IntelligenceType,
  { label: string; icon: typeof Brain }
> = {
  energy_anomaly: { label: "Energy", icon: Zap },
  environmental: { label: "Environment", icon: Droplets },
  maintenance_prediction: { label: "Maintenance", icon: Gauge },
  occupancy_pattern: { label: "Occupancy", icon: Shield },
  risk_score: { label: "Risk", icon: Activity },
};

export function IntelligenceCard({ item }: { item: IntelligenceItem }) {
  const { border, bg, text, badge, icon: SevIcon } = SEVERITY[item.severity];
  const { label: typeLabel, icon: TypeIcon } = TYPE_CONFIG[item.type] ?? {
    label: item.type,
    icon: Brain,
  };

  return (
    <div
      className={cn(
        "border-l-4 rounded-r-xl p-4 bg-surface border border-border",
        border,
        bg,
      )}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className={cn(
              "flex items-center gap-1 font-mono text-xs px-2 py-0.5 rounded-full border",
              badge,
            )}
          >
            <SevIcon size={10} />
            {item.severity.charAt(0).toUpperCase() + item.severity.slice(1)}
          </span>
          <span className="flex items-center gap-1 font-mono text-xs px-2 py-0.5 rounded-full bg-surface-2 border border-border text-text-3">
            <TypeIcon size={10} />
            {typeLabel}
          </span>
        </div>
        {item.metric != null && (
          <span
            className={cn("font-mono text-sm font-medium flex-shrink-0", text)}
          >
            {item.metric % 1 === 0 ? item.metric : item.metric.toFixed(1)}{" "}
            <span className="text-xs font-normal text-text-3">{item.unit}</span>
          </span>
        )}
      </div>

      <p className="font-body font-normal text-sm text-text mb-1">
        {item.title}
      </p>
      <p className="font-body font-light text-xs text-text-2 leading-relaxed mb-3">
        {item.detail}
      </p>

      <div className="flex items-center justify-between">
        <Link
          href={`/properties/${item.property_id}`}
          className="flex items-center gap-1 font-mono text-xs text-text-3 hover:text-text-2 transition-colors"
        >
          <MapPin size={10} />
          {item.property_name}
        </Link>
        <p className="font-mono text-xs text-text-3">
          {format(new Date(item.generated_at), "d MMM, HH:mm")}
        </p>
      </div>
    </div>
  );
}
