interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  sub?: string;
  primary?: React.ReactNode;
  secondary?: React.ReactNode;
}

export function PageHeader({
  eyebrow,
  title,
  sub,
  primary,
  secondary,
}: PageHeaderProps) {
  return (
    <div className="px-7 py-5 flex items-end justify-between gap-4 border-b border-border bg-surface flex-wrap sticky top-0 z-10">
      <div className="min-w-0">
        {eyebrow && (
          <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 mb-1.5 m-0">
            {eyebrow}
          </p>
        )}
        <h1 className="font-serif text-[26px] leading-[1.15] tracking-[-0.01em] text-text m-0">
          {title}
        </h1>
        {sub && <p className="text-[12px] text-text-3 mt-1 m-0">{sub}</p>}
      </div>
      {(primary ?? secondary) && (
        <div className="flex gap-2 items-center">
          {secondary}
          {primary}
        </div>
      )}
    </div>
  );
}
