"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { AlertTriangle, Cpu } from "lucide-react";
import type { Property, PropertyStatus } from "@/lib/types";
import { cn } from "@/lib/utils";
import { coverUrl } from "@/lib/cover";

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
        <div className="bg-surface border border-border rounded-xl overflow-hidden cursor-pointer hover:border-border-strong elevate-hover relative">
          {/* Cover photo with scrim + name overlay */}
          <div
            className="h-28 bg-surface-2 bg-cover bg-center relative"
            style={{
              backgroundImage: `linear-gradient(to top, rgba(26,26,23,0.62) 0%, rgba(26,26,23,0.05) 60%), url('${coverUrl(property.id)}')`,
            }}
          >
            {/* Frosted status pill */}
            <div className="absolute top-3 left-3 flex items-center gap-1.5 bg-surface/80 backdrop-blur-md rounded-full pl-2 pr-2.5 py-1 border border-white/30">
              <span className={cn("w-2 h-2 rounded-full flex-shrink-0", dot)} />
              <span className="font-body font-light text-[11px] text-text-2">
                {label}
              </span>
            </div>

            {/* Property name on image */}
            <p className="absolute bottom-2.5 left-4 right-4 font-display italic text-[18px] text-white leading-tight truncate drop-shadow">
              {property.name}
            </p>
          </div>

          {/* Card body */}
          <div className="px-5 pt-3 pb-4">
            <p className="font-body font-light text-xs text-text-3 truncate mb-3">
              {property.address.split(",").slice(-2).join(",").trim()}
            </p>

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
        </div>
      </Link>
    </motion.div>
  );
}
