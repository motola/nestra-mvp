"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Root error:", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-bg flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-[420px] bg-surface border border-border rounded-card p-8 shadow-md">
        <h1 className="font-serif text-[26px] leading-[1.2] text-text m-0 mb-2">
          Something went wrong
        </h1>
        <p className="text-[13px] text-text-3 mb-6 m-0">
          {error.message || "An unexpected error occurred."}
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
