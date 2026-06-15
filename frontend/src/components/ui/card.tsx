import { cn } from "@/lib/cn";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
  onClick?: () => void;
}

export function Card({ children, className, hoverable, onClick }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "bg-surface border border-border rounded-card",
        hoverable &&
          "transition-colors duration-[120ms] hover:border-border-strong",
        onClick && "cursor-pointer",
        className,
      )}
    >
      {children}
    </div>
  );
}

interface SectionHeadProps {
  title: string;
  sub?: string;
  right?: React.ReactNode;
  className?: string;
}

export function SectionHead({
  title,
  sub,
  right,
  className,
}: SectionHeadProps) {
  return (
    <div
      className={cn(
        "flex items-baseline justify-between mb-3 gap-4 flex-wrap",
        className,
      )}
    >
      <div className="min-w-0">
        <h2 className="text-[18px] font-semibold text-text leading-[1.3] m-0">
          {title}
        </h2>
        {sub && (
          <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 mt-1 m-0">
            {sub}
          </p>
        )}
      </div>
      {right && (
        <div className="flex items-center gap-2 flex-wrap">{right}</div>
      )}
    </div>
  );
}

export function MonoLabel({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "font-mono text-[10px] uppercase tracking-[0.08em] text-text-3",
        className,
      )}
    >
      {children}
    </span>
  );
}
