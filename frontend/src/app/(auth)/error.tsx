"use client";

import { useEffect } from "react";

export default function AuthError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Auth error:", error);
  }, [error]);

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
        <h1 className="font-serif text-[26px] leading-[1.2] text-text m-0 mb-1">
          Error loading page
        </h1>
        <p className="text-[13px] text-text-3 mb-6 m-0">
          {error.message || "Failed to load. Please try again."}
        </p>
        <button
          onClick={reset}
          className="w-full bg-accent text-white rounded-[9px] px-3 py-2 text-[13px] font-medium hover:opacity-90 transition"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
