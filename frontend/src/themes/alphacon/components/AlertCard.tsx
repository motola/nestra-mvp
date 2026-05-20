"use client";

import { AlertTriangle, CheckCircle, X, XCircle } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";
import { format } from "date-fns";
import type { Alert, AlertSeverity } from "@/lib/types";
import { cn } from "@/lib/utils";

const SEVERITY: Record<
  AlertSeverity,
  { border: string; bg: string; text: string; icon: typeof CheckCircle }
> = {
  info: {
    border: "border-l-green",
    bg: "",
    text: "text-green",
    icon: CheckCircle,
  },
  warning: {
    border: "border-l-amber",
    bg: "",
    text: "text-amber",
    icon: AlertTriangle,
  },
  critical: {
    border: "border-l-red",
    bg: "bg-red-bg",
    text: "text-red",
    icon: XCircle,
  },
};

export function AlertCard({
  alert,
  onDismiss,
  index = 0,
}: {
  alert: Alert;
  onDismiss?: () => void;
  index?: number;
}) {
  const { border, bg, text, icon: Icon } = SEVERITY[alert.severity];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ x: 40, opacity: 0 }}
      transition={{ duration: 0.2, delay: index * 0.03 }}
      className={cn(
        "border-l-4 rounded-r-xl p-4 flex items-start gap-3 bg-surface border border-border",
        border,
        bg,
      )}
    >
      <Icon size={15} className={cn("flex-shrink-0 mt-0.5", text)} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1 flex-wrap">
          <Link
            href={`/properties/${alert.property_id}/devices/${alert.device_id}`}
            className="font-body font-normal text-sm text-text hover:underline"
          >
            {alert.device_name}
          </Link>
          <span className="text-text-3">·</span>
          <p className="font-body font-light text-xs text-text-3 truncate">
            {alert.property_name}
          </p>
        </div>
        <p className="font-body font-light text-sm text-text-2">
          {alert.message}
        </p>
        <p className="font-mono text-xs text-text-3 mt-1">
          {format(new Date(alert.created_at), "d MMM, HH:mm")}
        </p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 text-text-3 hover:text-text-2 transition-colors"
          title="Dismiss"
        >
          <X size={15} />
        </button>
      )}
    </motion.div>
  );
}
