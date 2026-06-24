"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

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
  className,
}: {
  label: string;
  value: number | string;
  unit?: string;
  sub?: string;
  icon?: React.ElementType;
  animate?: boolean;
  className?: string;
}) {
  const numValue = typeof value === "number" ? value : 0;
  const animated = useCountUp(animate ? numValue : 0);
  const display = animate ? animated : value;

  return (
    <div
      className={cn(
        "bg-surface border border-border rounded-xl p-5 elevate elevate-hover",
        className,
      )}
    >
      <div className="flex items-start justify-between mb-4">
        <span className="font-body font-normal text-xs uppercase tracking-widest text-text-3">
          {label}
        </span>
        {Icon && (
          <span className="w-8 h-8 rounded-lg bg-surface-2 border border-border/60 flex items-center justify-center text-text-2 flex-shrink-0">
            <Icon size={15} />
          </span>
        )}
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className="font-display text-[34px] leading-none text-text tabular-nums">
          {display}
        </span>
        {unit && <span className="font-mono text-xs text-text-3">{unit}</span>}
      </div>
      {sub && <p className="font-mono text-xs text-text-3 mt-2">{sub}</p>}
    </div>
  );
}
