import { cn } from "@/lib/cn";

export type TagVariant = "ok" | "warn" | "alert" | "neutral" | "graphite";

interface TagProps {
  variant?: TagVariant;
  withDot?: boolean;
  className?: string;
  children: React.ReactNode;
}

const variants: Record<TagVariant, string> = {
  ok: "bg-green-bg text-green",
  warn: "bg-amber-bg text-amber",
  alert: "bg-red-bg text-red",
  neutral: "bg-surface-2 text-text-2 border border-border",
  graphite: "bg-graphite text-[#f4f1eb]",
};

const dotColors: Record<TagVariant, string> = {
  ok: "bg-green",
  warn: "bg-amber",
  alert: "bg-red",
  neutral: "bg-text-2",
  graphite: "bg-[#f4f1eb]",
};

export function Tag({
  variant = "neutral",
  withDot = false,
  className,
  children,
}: TagProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 whitespace-nowrap rounded-tag",
        "font-mono text-[10px] uppercase tracking-[0.08em] font-medium",
        "px-[9px] py-[3px]",
        variants[variant],
        className,
      )}
    >
      {withDot && (
        <span
          className={cn(
            "w-1.5 h-1.5 rounded-full shrink-0",
            dotColors[variant],
          )}
        />
      )}
      {children}
    </span>
  );
}
