"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { AlertTriangle, Cpu } from "lucide-react";
import type { Property, PropertyStatus } from "@/lib/types";
import { cn } from "@/lib/utils";
import { seededSparklineValues } from "./Sparkline";
import { PropertyIllustration } from "../ui/PropertyIllustration";

const STATUS_GRADIENT: Record<PropertyStatus, string> = {
  all_clear:
    "linear-gradient(to bottom, rgba(45,107,45,0.03) 0%, transparent 60%)",
  needs_attention:
    "linear-gradient(to bottom, rgba(154,94,21,0.04) 0%, transparent 60%)",
  critical:
    "linear-gradient(to bottom, rgba(139,32,32,0.05) 0%, transparent 60%)",
};

const STATUS_LINE: Record<PropertyStatus, string> = {
  all_clear: "#2d6b2d",
  needs_attention: "#9a5e15",
  critical: "#8b2020",
};

const STATUS_DOT: Record<PropertyStatus, string> = {
  all_clear: "bg-green",
  needs_attention: "bg-amber",
  critical: "bg-red",
};

const STATUS_LABEL: Record<PropertyStatus, string> = {
  all_clear: "All Clear",
  needs_attention: "Needs Attention",
  critical: "Critical",
};

function BottomSparkline({
  seed,
  status,
}: {
  seed: string;
  status: PropertyStatus;
}) {
  const vals = seededSparklineValues(seed);
  const min = Math.min(...vals);
  const max = Math.max(...vals);
  const range = max - min || 1;
  const h = 32;
  const w = 100;
  const pts = vals
    .map((v, i) => {
      const x = (i / (vals.length - 1)) * w;
      const y = h - ((v - min) / range) * (h - 4) - 2;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      preserveAspectRatio="none"
      className="w-full"
      style={{ height: h }}
    >
      <defs>
        <linearGradient id={`spk-${seed}`} x1="0" y1="0" x2="0" y2="1">
          <stop
            offset="0%"
            stopColor={STATUS_LINE[status]}
            stopOpacity="0.15"
          />
          <stop offset="100%" stopColor={STATUS_LINE[status]} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polyline
        points={pts}
        fill="none"
        stroke={STATUS_LINE[status]}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function PropertyCard({
  property,
  index = 0,
}: {
  property: Property;
  index?: number;
}) {
  const dot = STATUS_DOT[property.status];
  const label = STATUS_LABEL[property.status];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.06, ease: "easeOut" }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
    >
      <Link href={`/properties/${property.id}`}>
        <div
          className="bg-surface border border-border rounded-xl overflow-hidden cursor-pointer hover:border-border-strong elevate-hover relative"
          style={{
            background:
              STATUS_GRADIENT[property.status] + ", var(--color-surface)",
          }}
        >
          {/* Card body */}
          <div className="px-5 pt-5 pb-4 relative">
            {/* SVG illustration top-right */}
            <div className="absolute top-3 right-3 text-border opacity-40 pointer-events-none">
              <PropertyIllustration name={property.name} />
            </div>

            {/* Status row */}
            <div className="flex items-center gap-2 mb-3">
              <span className={cn("w-2 h-2 rounded-full flex-shrink-0", dot)} />
              <span className="font-body font-light text-xs text-text-3">
                {label}
              </span>
            </div>

            {/* Property name */}
            <p className="font-display italic text-[18px] text-text leading-tight mb-1 pr-20">
              {property.name}
            </p>

            {/* Address */}
            <p className="font-body font-light text-xs text-text-3 truncate mb-4">
              {property.address.split(",").slice(-2).join(",").trim()}
            </p>

            {/* Divider */}
            <div className="border-t border-border mb-3" />

            {/* Stats row */}
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1 font-mono text-xs text-text-2">
                <Cpu size={10} className="text-text-3" />
                {property.device_count} device
                {property.device_count !== 1 ? "s" : ""}
              </span>
              {property.alert_count > 0 && (
                <span className="flex items-center gap-1 font-mono text-xs text-amber ml-auto">
                  <AlertTriangle size={10} />
                  {property.alert_count} alert
                  {property.alert_count !== 1 ? "s" : ""}
                </span>
              )}
            </div>
          </div>

          {/* Full-width sparkline strip */}
          <div className="-mx-0 mt-0">
            <BottomSparkline seed={property.id} status={property.status} />
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
