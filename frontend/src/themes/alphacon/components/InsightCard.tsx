"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle, Loader2, XCircle } from "lucide-react";
import { format } from "date-fns";
import { insightsApi } from "@/lib/api";
import type { Insight, InsightSeverity } from "@/lib/types";
import { cn } from "@/lib/utils";

const SEVERITY_CONFIG: Record<
  InsightSeverity,
  { border: string; bg: string; text: string; icon: typeof CheckCircle }
> = {
  info: {
    border: "border-l-green",
    bg: "bg-green-bg",
    text: "text-green",
    icon: CheckCircle,
  },
  warning: {
    border: "border-l-amber",
    bg: "bg-amber-bg",
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

export function InsightCard({ deviceId }: { deviceId: string }) {
  const {
    data: insight,
    isLoading,
    isError,
  } = useQuery<Insight>({
    queryKey: ["insight", deviceId],
    queryFn: () => insightsApi.get(deviceId),
    staleTime: 15 * 60 * 1000,
  });

  return (
    <div className="bg-surface border border-border rounded-xl p-5">
      <div className="flex items-center gap-2 mb-3">
        <p className="font-body font-normal text-sm text-text">AI Insight</p>
        <span className="font-mono text-xs text-text-3 bg-surface-2 border border-border px-2 py-0.5 rounded-full">
          {insight?.model_used === "demo" ? "demo" : "Claude"}
        </span>
        {insight?.cached && (
          <span className="font-mono text-xs text-text-3">cached</span>
        )}
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 text-text-3 text-sm">
          <Loader2 size={14} className="animate-spin" />
          <span className="font-body font-light">Generating insight…</span>
        </div>
      )}

      {isError && (
        <p className="font-body font-light text-sm text-text-3">
          Could not load insight. Add ANTHROPIC_API_KEY to enable AI analysis.
        </p>
      )}

      {insight &&
        (() => {
          const {
            border,
            bg,
            text,
            icon: Icon,
          } = SEVERITY_CONFIG[insight.severity];
          return (
            <div
              className={cn(
                "border-l-4 rounded-r-lg p-3 flex gap-2.5",
                border,
                bg,
              )}
            >
              <Icon size={15} className={cn("flex-shrink-0 mt-0.5", text)} />
              <div>
                <p className="font-body font-light text-sm text-text leading-relaxed">
                  {insight.message}
                </p>
                <p className="font-mono text-xs text-text-3 mt-1.5">
                  {format(new Date(insight.generated_at), "d MMM, HH:mm")}
                </p>
              </div>
            </div>
          );
        })()}
    </div>
  );
}
