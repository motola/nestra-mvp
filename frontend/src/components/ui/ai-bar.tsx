"use client";

import { useRouter } from "next/navigation";
import { ArrowRight } from "lucide-react";

interface AIBarProps {
  chips?: string[];
  placeholder?: string;
  compact?: boolean;
  href?: string;
}

const DEFAULT_CHIPS = [
  "energy report",
  "vacant units",
  "active alerts",
  "draft check-in",
];

export function AIBar({
  chips = DEFAULT_CHIPS,
  placeholder = "Ask anything about your portfolio — what's my total energy spend this week?",
  compact = false,
  href = "/agent",
}: AIBarProps) {
  const router = useRouter();

  return (
    <div
      onClick={() => router.push(href)}
      className="flex items-center gap-3 rounded-panel cursor-pointer"
      style={{
        background: "linear-gradient(180deg, #28241e 0%, #3a3530 100%)",
        padding: compact ? "12px 14px" : "14px 16px",
      }}
    >
      <div
        className="flex items-center justify-center shrink-0 rounded-[8px]"
        style={{
          width: compact ? 32 : 36,
          height: compact ? 32 : 36,
          background: "#3a3530",
        }}
      >
        <span
          className="w-[9px] h-[9px] rounded-full bg-green"
          style={{ boxShadow: "0 0 8px rgba(45,107,45,0.6)" }}
        />
      </div>

      <input
        readOnly
        className="flex-1 bg-transparent border-none outline-none min-w-0 italic font-sans cursor-pointer"
        style={{ color: "#a39d8e", fontSize: compact ? 13 : 14 }}
        placeholder={placeholder}
        onClick={(e) => e.stopPropagation()}
      />

      {!compact && (
        <div className="flex gap-1.5">
          {chips.map((c) => (
            <button
              key={c}
              onClick={(e) => e.stopPropagation()}
              className="font-mono text-[10px] uppercase tracking-[0.08em] font-medium whitespace-nowrap rounded-tag px-[10px] py-[5px] border-0 cursor-pointer"
              style={{ background: "#3a3530", color: "#a39d8e" }}
            >
              {c}
            </button>
          ))}
        </div>
      )}

      <button
        onClick={(e) => {
          e.stopPropagation();
          router.push(href);
        }}
        className="w-[30px] h-[30px] rounded-[8px] bg-bg text-text flex items-center justify-center border-0 cursor-pointer shrink-0"
      >
        <ArrowRight size={14} strokeWidth={1.5} />
      </button>
    </div>
  );
}
