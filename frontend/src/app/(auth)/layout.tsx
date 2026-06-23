// Auth layout — no sidebar or top nav, just a centered card on the parchment canvas

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-bg flex flex-col items-center justify-center px-4">
      {/* Brand mark */}
      <div className="flex items-center gap-2.5 mb-8">
        <div className="w-7 h-7 rounded-[7px] bg-graphite flex items-center justify-center relative shrink-0">
          <span className="font-serif text-[19px] text-white leading-none select-none">
            A
          </span>
          <span className="absolute top-[3px] right-[3px] w-[5px] h-[5px] rounded-full bg-accent" />
        </div>
        <span className="font-serif text-[22px] tracking-[-0.01em] text-text">
          Alphacon
        </span>
      </div>

      {/* Card */}
      <div className="w-full max-w-[420px] bg-surface border border-border rounded-card p-8 shadow-md">
        {children}
      </div>
    </div>
  );
}
