"use client";

import { useState } from "react";
import { ArrowRight, Check, Settings } from "lucide-react";
import { SectionHead } from "@/components/ui/card";
import { Tag } from "@/components/ui/tag";
import { cn } from "@/lib/cn";

const QUESTIONS = [
  {
    id: "energy",
    q: "What's my energy spend this week?",
    tool: "get_portfolio_energy",
    answer:
      "£77.20 across 12 properties — 8% below your weekly average. Maple Court is the largest at £19.40.",
  },
  {
    id: "vacant",
    q: "Which units are vacant right now?",
    tool: "list_units",
    answer:
      "3 vacant: Maple Court Flat 3B + Flat 1A, and Albany Mews Flat 4. Flat 3B still had heating on.",
  },
  {
    id: "offline",
    q: "Are any devices offline?",
    tool: "get_device_health",
    answer:
      "2 offline: Northbrook Mill thermostats (Flat 2A, 4B) since 06:47, and 1 unreachable sensor at Maple Court.",
  },
  {
    id: "approve",
    q: "What's waiting for my approval?",
    tool: "list_pending_actions",
    answer:
      "2 items: turn off vacant heating at Maple Court, and a drafted check-in message for Larkspur Flat 1.",
  },
  {
    id: "attention",
    q: "Which properties need attention?",
    tool: "list_attention",
    answer:
      "2 right now: Maple Court (vacant heating) and Northbrook Mill (2 thermostats offline since 06:47).",
  },
  {
    id: "overnight",
    q: "Summarize overnight activity",
    tool: "get_activity_digest",
    answer:
      "Quiet night. Agent cooled 1 vacant unit, a hub dropped at Northbrook, and 1 check-in is overdue.",
  },
];

export function QuickQuestions() {
  const [open, setOpen] = useState<string | null>(null);

  return (
    <section>
      <SectionHead
        title="Quick questions"
        sub="ONE-TAP LOOKUPS · CACHED · NO REASONING SPEND"
        right={
          <button className="flex items-center gap-1.5 text-[12px] text-text-2 font-medium bg-transparent border-0 cursor-pointer px-[10px] py-[5px] rounded-[9px] hover:bg-surface-2 transition-colors duration-[120ms]">
            <Settings size={12} strokeWidth={1.5} />
            Customize
          </button>
        }
      />
      <div className="grid grid-cols-3 gap-3">
        {QUESTIONS.map((item) => {
          const isOpen = open === item.id;
          return (
            <div
              key={item.id}
              onClick={() => setOpen(isOpen ? null : item.id)}
              className={cn(
                "bg-surface border rounded-card p-4 cursor-pointer flex flex-col gap-2.5",
                "transition-colors duration-[120ms]",
                isOpen
                  ? "border-border-strong"
                  : "border-border hover:border-border-strong",
              )}
            >
              <div className="flex items-start justify-between gap-2.5">
                <span className="text-[13px] font-medium text-text leading-[1.4] flex-1">
                  {item.q}
                </span>
                <span
                  className={cn(
                    "w-6 h-6 rounded-[7px] shrink-0 flex items-center justify-center transition-colors duration-[120ms]",
                    isOpen
                      ? "bg-graphite text-[#fbf9f4]"
                      : "bg-surface-2 text-text-3",
                  )}
                >
                  {isOpen ? (
                    <Check size={12} strokeWidth={1.5} />
                  ) : (
                    <ArrowRight size={12} strokeWidth={1.5} />
                  )}
                </span>
              </div>

              {isOpen ? (
                <div className="border-t border-dashed border-border pt-2.5 flex flex-col gap-2">
                  <p className="text-[12px] text-text-2 leading-[1.6] m-0">
                    {item.answer}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3">
                      {item.tool} · 0 reasoning tokens
                    </span>
                    <button
                      onClick={(e) => e.stopPropagation()}
                      className="text-[11px] text-graphite font-medium flex items-center gap-1 bg-transparent border-0 cursor-pointer"
                    >
                      Open in agent <ArrowRight size={11} strokeWidth={1.5} />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3">
                    {item.tool}
                  </span>
                  <Tag variant="ok">instant</Tag>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
