"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { Sparkline } from "./Sparkline";

function useCountUp(target: number, duration = 800) {
  const [value, setValue] = useState(0);
  const rafRef = useRef<number>(0);
  useEffect(() => {
    const start = performance.now();
    const step = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * target));
      if (progress < 1) rafRef.current = requestAnimationFrame(step);
    };
    rafRef.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(rafRef.current);
  }, [target, duration]);
  return value;
}

export function StatCard({
  label,
  value,
  unit,
  sub,
  icon: Icon,
  animate = false,
  trend,
  className,
}: {
  label: string;
  value: number | string;
  unit?: string;
  sub?: string;
  icon?: React.ElementType;
  animate?: boolean;
  trend?: string;
  className?: string;
}) {
  const numValue = typeof value === "number" ? value : 0;
  const animated = useCountUp(animate ? numValue : 0);
  const display = animate ? animated : value;

  return (
    <div
      className={cn(
        "bg-surface border border-border rounded-xl p-4",
        className,
      )}
    >
      {Icon && (
        <div className="flex items-center gap-1.5 text-text-3 mb-2">
          <Icon size={13} />
          <span className="font-body font-normal text-xs uppercase tracking-widest">
            {label}
          </span>
        </div>
      )}
      {!Icon && (
        <p className="font-body font-normal text-xs uppercase tracking-widest text-text-3 mb-2">
          {label}
        </p>
      )}
      <div className="flex items-end justify-between gap-2">
        <div className="flex items-baseline gap-1.5">
          <span className="font-mono text-2xl text-text tabular-nums">
            {display}
          </span>
          {unit && (
            <span className="font-mono text-xs text-text-3">{unit}</span>
          )}
        </div>
        {trend && (
          <span className="text-text-3 mb-0.5">
            <Sparkline seed={trend} width={58} height={22} />
          </span>
        )}
      </div>
      {sub && <p className="font-mono text-xs text-text-3 mt-1">{sub}</p>}
    </div>
  );
}
