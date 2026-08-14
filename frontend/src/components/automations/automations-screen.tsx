"use client"; // Client: filter chips and per-automation toggle state

import { useState } from "react";
import { Plus, Sparkles, Zap, Settings } from "lucide-react";
import { cn } from "@/lib/cn";
import { AUTOMATIONS } from "@/lib/fixtures";
import type { Automation } from "@/lib/fixtures";
import { Button } from "@/components/ui/button";
import { Tag } from "@/components/ui/tag";
import { Card, SectionHead, MonoLabel } from "@/components/ui/card";
import { StatCard } from "@/components/ui/stat-card";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyDataState } from "@/components/ui/empty-state";
import { useDemoMode } from "@/lib/use-demo-mode";

// ─── Toggle switch ────────────────────────────────────────────────────────────

function Toggle({
  enabled,
  onToggle,
}: {
  enabled: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      onClick={onToggle}
      aria-pressed={enabled}
      aria-label={enabled ? "Disable automation" : "Enable automation"}
      className={cn(
        "relative w-11 h-6 rounded-full cursor-pointer border-0 shrink-0",
        "transition-colors duration-200",
        enabled ? "bg-graphite" : "bg-surface-2 border border-border",
      )}
    >
      <div
        className={cn(
          "absolute top-[3px] w-[18px] h-[18px] rounded-full bg-white",
          "transition-[left] duration-200",
          enabled ? "left-[23px]" : "left-[3px]",
        )}
        style={{ boxShadow: "0 1px 2px rgba(16,24,40,0.2)" }}
      />
    </button>
  );
}

// ─── Agent suggestions panel ──────────────────────────────────────────────────

const SUGGESTIONS = [
  {
    id: "s1",
    name: "Weekday pre-arrival schedule",
    trigger: "Mon–Fri · 16:00",
    why: "Occupants return at ~16:30 four of five weekdays. Warming earlier cuts the morning spike.",
  },
  {
    id: "s2",
    name: "Quiet hours for Ash Cottage",
    trigger: "Daily · 23:00 → 07:00",
    why: "Short-let in a residential street; volume complaints last quarter.",
  },
  {
    id: "s3",
    name: "Weekly leak check ping",
    trigger: "Sundays · 09:00",
    why: "Reduce time-to-detection with a low-cost reminder.",
  },
];

function AgentSuggestions() {
  return (
    <section
      className="border border-border rounded-panel p-[18px]"
      style={{
        background:
          "linear-gradient(180deg, var(--color-surface) 0%, var(--color-surface-2) 100%)",
      }}
    >
      <div className="flex items-center gap-2 mb-3.5">
        <Sparkles size={15} strokeWidth={1.5} className="text-graphite" />
        <h2 className="text-[16px] font-semibold text-text m-0">
          The agent wants to set up 3 automations
        </h2>
        <MonoLabel className="ml-auto">review · tweak · approve</MonoLabel>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {SUGGESTIONS.map((s) => (
          <Card key={s.id} className="p-4 flex flex-col gap-2.5">
            <MonoLabel className="text-graphite">Proposed</MonoLabel>
            <p className="font-serif text-[17px] text-text m-0">{s.name}</p>
            <MonoLabel>{s.trigger}</MonoLabel>
            <p className="text-[12px] text-text-2 leading-[1.55] m-0">
              {s.why}
            </p>
            <div className="flex gap-2 mt-1">
              <Button variant="tagPrim" size="sm">
                Approve
              </Button>
              <Button variant="tagSec" size="sm">
                Tweak
              </Button>
              <Button variant="tagSec" size="sm">
                Dismiss
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </section>
  );
}

// ─── Automation card ──────────────────────────────────────────────────────────

const META_KEYS = ["trigger", "actions", "scope", "last run"] as const;

function AutomationCard({
  item,
  enabled,
  onToggle,
}: {
  item: Automation;
  enabled: boolean;
  onToggle: () => void;
}) {
  const metaValues: Record<(typeof META_KEYS)[number], string> = {
    trigger: item.trigger,
    actions: String(item.actions),
    scope: item.scope,
    "last run": item.lastRun,
  };

  return (
    <Card hoverable className="p-[18px]">
      <div className="flex items-center gap-4">
        <div
          className={cn(
            "w-9 h-9 rounded-[8px] shrink-0 flex items-center justify-center",
            enabled ? "bg-graphite" : "bg-surface-2",
          )}
        >
          {item.source === "AGENT" ? (
            <Sparkles
              size={16}
              strokeWidth={1.5}
              color={enabled ? "#ffffff" : "var(--color-text-3)"}
            />
          ) : (
            <Zap
              size={16}
              strokeWidth={1.5}
              color={enabled ? "#ffffff" : "var(--color-text-3)"}
            />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="font-serif text-[18px] text-text">
              {item.name}
            </span>
            {item.source === "AGENT" ? (
              <Tag variant="graphite" withDot>
                Set by agent
              </Tag>
            ) : (
              <Tag variant="neutral">Manual</Tag>
            )}
            {!enabled && <Tag variant="neutral">paused</Tag>}
          </div>

          <div className="flex gap-3.5 mt-2 flex-wrap">
            {META_KEYS.map((k) => (
              <span key={k} className="text-[12px] text-text-2">
                <MonoLabel className="mr-1">{k}</MonoLabel>
                {metaValues[k]}
              </span>
            ))}
          </div>
        </div>

        <Button variant="ghost" size="sm" icon={Settings}>
          Tweak
        </Button>

        <div className="text-right shrink-0">
          <p className="font-mono text-[16px] font-semibold [font-variant-numeric:tabular-nums] text-text m-0">
            {item.runs}
          </p>
          <MonoLabel>runs · 90d</MonoLabel>
        </div>

        <Toggle enabled={enabled} onToggle={onToggle} />
      </div>
    </Card>
  );
}

// ─── Filter chips ─────────────────────────────────────────────────────────────

type AutoFilter = "all" | "agent" | "manual" | "paused";

const FILTER_OPTS: { id: AutoFilter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "agent", label: "Set by agent" },
  { id: "manual", label: "Manual" },
  { id: "paused", label: "Paused" },
];

function FilterChips({
  active,
  onChange,
  counts,
}: {
  active: AutoFilter;
  onChange: (f: AutoFilter) => void;
  counts: Record<AutoFilter, number>;
}) {
  return (
    <div className="flex gap-1.5 items-center flex-wrap">
      {FILTER_OPTS.map(({ id, label }) => (
        <button
          key={id}
          onClick={() => onChange(id)}
          className={cn(
            "inline-flex items-center gap-2 rounded-[9px] px-3 py-[5px] text-[12px] font-medium",
            "border cursor-pointer font-sans transition-colors duration-[120ms]",
            active === id
              ? "bg-graphite text-white border-graphite"
              : "bg-surface text-text-2 border-border hover:border-border-strong",
          )}
        >
          {label}
          <span className="font-mono text-[10px] opacity-80">{counts[id]}</span>
        </button>
      ))}
    </div>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

export function AutomationsScreen() {
  const { demoMode } = useDemoMode();
  const [filter, setFilter] = useState<AutoFilter>("all");
  const [paused, setPaused] = useState<Set<string>>(
    new Set(AUTOMATIONS.filter((a) => !a.enabled).map((a) => a.id)),
  );

  if (!demoMode) {
    return (
      <>
        <PageHeader
          eyebrow="WORKSPACE"
          title="Automations"
          sub="0 automations active"
          primary={
            <Button variant="primary" icon={Plus}>
              Create automation
            </Button>
          }
        />
        <EmptyDataState
          title="No automations created"
          description="Set up your first automation to streamline property management."
        />
      </>
    );
  }

  function toggle(id: string) {
    setPaused((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  const isEnabled = (a: Automation) => !paused.has(a.id);

  const counts: Record<AutoFilter, number> = {
    all: AUTOMATIONS.length,
    agent: AUTOMATIONS.filter((a) => a.source === "AGENT").length,
    manual: AUTOMATIONS.filter((a) => a.source === "MANUAL").length,
    paused: paused.size,
  };

  const filtered = AUTOMATIONS.filter((a) => {
    if (filter === "agent") return a.source === "AGENT";
    if (filter === "manual") return a.source === "MANUAL";
    if (filter === "paused") return paused.has(a.id);
    return true;
  });

  const activeCount = AUTOMATIONS.length - paused.size;
  const agentCount = AUTOMATIONS.filter((a) => a.source === "AGENT").length;

  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Agentic automations"
        sub="Where the agent's automations live. Set up from the Intelligence pane — or build and tweak them by hand."
        primary={
          <Button variant="primary" icon={Plus}>
            New automation
          </Button>
        }
        secondary={
          <Button variant="secondary" icon={Sparkles}>
            Ask the agent to build one
          </Button>
        }
      />

      <div className="px-7 pt-5 pb-8 flex flex-col gap-5">
        <div className="grid grid-cols-4 gap-3">
          <StatCard
            label="Active"
            value={activeCount}
            sub={`${paused.size} paused`}
          />
          <StatCard
            label="Set by agent"
            value={agentCount}
            sub="From Intelligence"
          />
          <StatCard label="Runs · 24h" value={34} sub="2 awaiting approval" />
          <StatCard
            label="New suggestions"
            value={3}
            sub="Patterns detected this week"
          />
        </div>

        <AgentSuggestions />

        <div>
          <SectionHead
            title="Live automations"
            sub="TRIGGER → CONDITIONS → ACTIONS · EDIT ANY BY HAND"
            right={
              <FilterChips
                active={filter}
                onChange={setFilter}
                counts={counts}
              />
            }
          />
          <div className="flex flex-col gap-2">
            {filtered.map((a) => (
              <AutomationCard
                key={a.id}
                item={a}
                enabled={isEnabled(a)}
                onToggle={() => toggle(a.id)}
              />
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
