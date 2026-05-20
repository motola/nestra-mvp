import { cn } from "@/lib/utils";

type BadgeVariant = "green" | "amber" | "red" | "neutral" | "graphite";

const VARIANTS: Record<BadgeVariant, string> = {
  green: "bg-green-bg text-green border-green/20",
  amber: "bg-amber-bg text-amber border-amber/20",
  red: "bg-red-bg text-red border-red/20",
  neutral: "bg-surface-2 text-text-3 border-border",
  graphite: "bg-graphite text-surface border-transparent",
};

export function Badge({
  children,
  variant = "neutral",
  className,
}: {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 font-mono text-xs px-2 py-0.5 rounded-full border",
        VARIANTS[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}
