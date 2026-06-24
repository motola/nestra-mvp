"use client";

// Client: the prominent agent surface shown on every authenticated page.
// Submitting dispatches a `nestra:ask` event that AgentChat listens for.

import { ArrowUp } from "lucide-react";
import { useState } from "react";

const CHIPS = ["Active alerts", "Maintenance due", "Unlocked doors"];

function ask(prompt: string): void {
  if (!prompt.trim()) return;
  window.dispatchEvent(new CustomEvent("nestra:ask", { detail: prompt }));
}

export function AIBar() {
  const [value, setValue] = useState("");

  function submit(prompt: string): void {
    ask(prompt);
    setValue("");
  }

  return (
    <div className="px-6 md:px-8 pt-5">
      <div className="max-w-6xl mx-auto bg-graphite/90 backdrop-blur-xl border border-white/5 shadow-lg shadow-graphite/10 rounded-2xl pl-3 pr-3 py-2.5 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-graphite-2 flex items-center justify-center relative flex-shrink-0">
          <span className="font-display italic text-surface text-lg leading-none">
            N
          </span>
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-green" />
        </div>

        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") submit(value);
          }}
          placeholder="Ask anything about your portfolio…"
          className="flex-1 min-w-0 bg-transparent outline-none border-none italic text-[15px] text-surface placeholder:text-text-3"
        />

        <div className="hidden md:flex items-center gap-2">
          {CHIPS.map((chip) => (
            <button
              key={chip}
              onClick={() => submit(chip)}
              className="font-mono text-[11px] text-text-3 bg-graphite-2 px-3 py-1.5 rounded-full hover:text-surface transition-colors whitespace-nowrap"
            >
              {chip}
            </button>
          ))}
        </div>

        <button
          onClick={() => submit(value)}
          aria-label="Ask the assistant"
          className="w-8 h-8 rounded-lg bg-surface flex items-center justify-center flex-shrink-0 hover:bg-surface-2 transition-colors"
        >
          <ArrowUp size={16} className="text-graphite" />
        </button>
      </div>
    </div>
  );
}
