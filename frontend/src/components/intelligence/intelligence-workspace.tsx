"use client"; // Client: chat tabs, messages, composer, quick-actions tray, activity slide-over

import { useState } from "react";
import {
  X,
  Plus,
  Sparkles,
  Zap,
  Building2,
  Monitor,
  Check,
  AlertTriangle,
  History,
  Mail,
  BookOpen,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { PROPERTIES } from "@/lib/fixtures";
import { Button } from "@/components/ui/button";
import { useDemoMode } from "@/lib/use-demo-mode";

// ─── Types ────────────────────────────────────────────────────────────────────

type Role = "you" | "ai";
type ActivityKind = "ok" | "warn" | "alert" | "neutral";

interface Message {
  id: string;
  role: Role;
  text: string;
}

interface Chat {
  id: string;
  title: string;
  when: string;
  messages: Message[];
}

interface QuickAction {
  id: string;
  Icon: LucideIcon;
  label: string;
  answer: string;
}

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const SEED_CHATS: Chat[] = [
  {
    id: "c_energy",
    title: "Energy spend this week",
    when: "12 min ago",
    messages: [
      {
        id: "m1",
        role: "you",
        text: "What was my energy spend this week and where did most of it go?",
      },
      {
        id: "m2",
        role: "ai",
        text: "Portfolio used 312 kWh last week — £77.20 total, 8% below your weekly average. Maple Court was the largest at £19.40, driven mostly by Flat 3B running heating while vacant. I turned that off Wednesday.",
      },
    ],
  },
  {
    id: "c_hub",
    title: "Northbrook hub restart",
    when: "1h ago",
    messages: [
      {
        id: "m3",
        role: "you",
        text: "Why are the Northbrook thermostats offline?",
      },
      {
        id: "m4",
        role: "ai",
        text: "Flat 2A and 4B stopped reporting at 06:47 — likely a hub disconnect. A remote restart usually clears it. Want me to restart the hub?",
      },
    ],
  },
  {
    id: "c_vacancy",
    title: "Maple Court vacancy options",
    when: "yesterday",
    messages: [
      {
        id: "m5",
        role: "you",
        text: "What are my options for the vacant Flat 3B?",
      },
      {
        id: "m6",
        role: "ai",
        text: "Three options: drop the thermostat to 14°C (saves ~£12/day), set a pre-arrival warm-up automation, or list it for short-let. I can set any of these up.",
      },
    ],
  },
];

const QUICK_ACTIONS: QuickAction[] = [
  {
    id: "energy",
    Icon: Zap,
    label: "Energy spend this week",
    answer:
      "£77.20 across 12 properties — 8% below your weekly average. Maple Court is the largest at £19.40.",
  },
  {
    id: "vacant",
    Icon: Building2,
    label: "Vacant units right now",
    answer:
      "3 vacant: Maple Court Flat 3B + Flat 1A, and Albany Mews Flat 4. Flat 3B still had heating on.",
  },
  {
    id: "offline",
    Icon: Monitor,
    label: "Devices offline",
    answer:
      "2 offline: Northbrook Mill thermostats (Flat 2A, 4B) since 06:47, and 1 unreachable sensor at Maple Court.",
  },
  {
    id: "approve",
    Icon: Check,
    label: "Waiting for my approval",
    answer:
      "2 items: turn off vacant heating at Maple Court, and the drafted weekly energy report.",
  },
  {
    id: "attention",
    Icon: AlertTriangle,
    label: "Properties needing attention",
    answer:
      "2 right now: Maple Court (vacant heating) and Northbrook Mill (2 thermostats offline).",
  },
  {
    id: "digest",
    Icon: History,
    label: "Overnight digest",
    answer:
      "Quiet night. Agent cooled 1 vacant unit, a hub dropped at Northbrook, and 1 report is awaiting review.",
  },
  {
    id: "report",
    Icon: Mail,
    label: "Run weekly energy report",
    answer: "Drafting the Monday summary for marcus@ and theo@…",
  },
  {
    id: "add",
    Icon: Plus,
    label: "Add a property",
    answer: "Opening the new-property form…",
  },
];

const RECENT_ACTIVITY: {
  time: string;
  who: string;
  what: string;
  kind: ActivityKind;
}[] = [
  {
    time: "08:42",
    who: "Agent",
    what: "Turned off heating in Maple Court Flat 3B",
    kind: "ok",
  },
  {
    time: "08:14",
    who: "Agent",
    what: "Detected vacant heating in Maple Court Flat 3B",
    kind: "warn",
  },
  {
    time: "07:30",
    who: "Marcus",
    what: "Approved March report for team email",
    kind: "neutral",
  },
  {
    time: "06:47",
    who: "System",
    what: "Northbrook Mill hub stopped responding",
    kind: "alert",
  },
  {
    time: "Y'day",
    who: "Agent",
    what: "Drafted check-in message for Larkspur House Flat 1",
    kind: "warn",
  },
];

const DOT_COLOR: Record<ActivityKind, string> = {
  ok: "bg-green",
  warn: "bg-amber",
  alert: "bg-red",
  neutral: "bg-text-3",
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

let _counter = 20;
function uid(prefix: string): string {
  return `${prefix}${_counter++}`;
}

// Placeholder until real Claude API integration lands
function cannedReply(text: string): string {
  const t = text.toLowerCase();
  if (/energy|spend|cost/.test(t))
    return "Portfolio is tracking £1,389 this month, 12% below budget. Maple Court is the largest line at £298. Want a breakdown by property?";
  if (/vacant|empty/.test(t))
    return "3 units are vacant right now: Maple Court Flat 3B + Flat 1A, and Albany Mews Flat 4. Flat 3B still had heating on — I can switch it off.";
  if (/offline|device|hub/.test(t))
    return "2 devices are offline: Northbrook Mill thermostats (Flat 2A, 4B) since 06:47. A remote hub restart usually clears it — shall I?";
  if (/report/.test(t))
    return "I've drafted the weekly energy summary for marcus@ and theo@. Review it and I'll schedule it for every Monday 08:00.";
  return "On it. I'll gather the data and show exactly what I checked — and I'll ask before anything that changes device state.";
}

// ─── Chat state hook ──────────────────────────────────────────────────────────

function useChatManager() {
  const empty: Chat = {
    id: "new0",
    title: "New chat",
    when: "now",
    messages: [],
  };
  const [chats, setChats] = useState<Chat[]>([empty, ...SEED_CHATS]);
  const [activeId, setActiveId] = useState<string>("new0");

  const activeChat = chats.find((c) => c.id === activeId) ?? chats[0];

  function newChat() {
    const id = uid("new");
    const fresh: Chat = { id, title: "New chat", when: "now", messages: [] };
    setChats((cs) => [fresh, ...cs]);
    setActiveId(id);
  }

  function closeTab(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    setChats((cs) => {
      const next = cs.filter((c) => c.id !== id);
      const safe = next.length
        ? next
        : [{ id: "new0", title: "New chat", when: "now", messages: [] }];
      if (id === activeId) setActiveId(safe[0].id);
      return safe;
    });
  }

  function send(text: string) {
    const msg = text.trim();
    if (!msg) return;
    setChats((cs) =>
      cs.map((c) => {
        if (c.id !== activeId) return c;
        const isFirst = c.messages.length === 0;
        return {
          ...c,
          title: isFirst
            ? msg.length > 36
              ? msg.slice(0, 36) + "…"
              : msg
            : c.title,
          when: "now",
          messages: [
            ...c.messages,
            { id: uid("m"), role: "you" as Role, text: msg },
            { id: uid("m"), role: "ai" as Role, text: cannedReply(msg) },
          ],
        };
      }),
    );
  }

  return { chats, activeId, activeChat, setActiveId, newChat, closeTab, send };
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function TabsBar({
  chats,
  activeId,
  onSelect,
  onClose,
  onNew,
  onActivity,
}: {
  chats: Chat[];
  activeId: string;
  onSelect: (id: string) => void;
  onClose: (id: string, e: React.MouseEvent) => void;
  onNew: () => void;
  onActivity: () => void;
}) {
  return (
    <div className="pl-0 pr-7 pt-3 bg-surface border-b border-border">
      <div className="flex items-end justify-between gap-4">
        <div className="flex gap-1 overflow-x-auto flex-1 min-w-0">
          {chats.map((chat) => {
            const on = chat.id === activeId;
            return (
              <button
                key={chat.id}
                role="tab"
                aria-selected={on}
                onClick={() => onSelect(chat.id)}
                className={cn(
                  "inline-flex items-center gap-2 shrink-0 px-3 py-2 -mb-px cursor-pointer",
                  "font-sans border rounded-t-[9px] max-w-[230px] transition-colors duration-[120ms]",
                  on
                    ? "bg-bg border-border text-text font-semibold"
                    : "bg-transparent border-transparent text-text-2 font-normal hover:text-text",
                )}
                style={on ? { borderBottomColor: "#f4f1eb" } : undefined}
              >
                <Sparkles
                  size={13}
                  strokeWidth={1.5}
                  className={
                    on ? "text-accent shrink-0" : "text-text-3 shrink-0"
                  }
                />
                <span className="text-[12px] truncate">{chat.title}</span>
                <span
                  onClick={(e) => onClose(chat.id, e)}
                  className="inline-flex text-text-3 hover:text-text rounded p-px shrink-0"
                  aria-label={`Close ${chat.title}`}
                >
                  <X size={12} strokeWidth={1.5} />
                </span>
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-2 shrink-0 pb-2">
          <button
            aria-label="Recent activity"
            onClick={onActivity}
            className="w-9 h-9 rounded-[9px] border border-border bg-surface text-text-2 flex items-center justify-center hover:border-border-strong transition-colors duration-[120ms]"
          >
            <History size={16} strokeWidth={1.5} />
          </button>
          <Button variant="secondary" icon={BookOpen} size="sm">
            History
          </Button>
          <Button variant="primary" icon={Plus} size="sm" onClick={onNew}>
            New chat
          </Button>
        </div>
      </div>
    </div>
  );
}

function EmptyState() {
  const totalUnits = PROPERTIES.reduce((s, p) => s + p.units, 0);
  const totalOcc = PROPERTIES.reduce((s, p) => s + p.occupied, 0);
  const totalAlerts = PROPERTIES.reduce((s, p) => s + p.alerts, 0);

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-7 py-10 text-center gap-4">
      <div className="w-[52px] h-[52px] rounded-[13px] bg-accent flex items-center justify-center">
        <Sparkles size={24} strokeWidth={1.5} color="#ffffff" />
      </div>
      <div className="max-w-[520px]">
        <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 m-0 mb-2.5">
          Hello Marcus
        </p>
        <h1
          className="font-serif text-text m-0"
          style={{ fontSize: 40, lineHeight: 1.12, letterSpacing: "-0.01em" }}
        >
          What would you like to do?
        </h1>
        <p className="text-[13px] text-text-2 mt-2.5 leading-[1.6] m-0">
          {PROPERTIES.length} properties · {totalUnits} units · {totalOcc}{" "}
          occupied · {totalAlerts} active alerts overnight. Ask about your
          portfolio or run an action — I&apos;ll show what I checked and ask
          before anything that changes device state.
        </p>
      </div>
    </div>
  );
}

function Transcript({ messages }: { messages: Message[] }) {
  return (
    <div className="flex-1 overflow-y-auto px-7 py-6 pb-2">
      <div className="max-w-[760px] mx-auto flex flex-col gap-5">
        {messages.map((m) => (
          <div key={m.id} className="flex gap-3.5 items-start">
            <span
              className={cn(
                "font-mono text-[10px] uppercase tracking-[0.08em] w-7 shrink-0 pt-[2px]",
                m.role === "ai" ? "text-green" : "text-text-3",
              )}
            >
              {m.role === "ai" ? "AI" : "You"}
            </span>
            <p
              className={cn(
                "flex-1 text-[14px] leading-[1.65] m-0",
                m.role === "ai" ? "text-text" : "text-text-2",
              )}
            >
              {m.text}
            </p>
          </div>
        ))}
        <div className="flex justify-center pt-1">
          <Button variant="ghost" size="sm" iconRight={Sparkles}>
            Open in full agent view
          </Button>
        </div>
      </div>
    </div>
  );
}

function QuickActionsTray({
  onSend,
  onClose,
}: {
  onSend: (text: string) => void;
  onClose: () => void;
}) {
  const [picked, setPicked] = useState<string | null>(null);
  const pickedAction = QUICK_ACTIONS.find((a) => a.id === picked);

  return (
    <div className="mb-3 bg-surface border border-border rounded-panel p-3.5 shadow-md">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Zap size={14} strokeWidth={1.5} className="text-graphite" />
          <span className="text-[13px] font-semibold text-text">
            Quick actions
          </span>
          <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3">
            cached · one tap · no reasoning spend
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-text-3 hover:text-text p-0.5"
          aria-label="Close quick actions"
        >
          <X size={16} strokeWidth={1.5} />
        </button>
      </div>

      <div className="grid grid-cols-4 gap-2">
        {QUICK_ACTIONS.map((a) => {
          const on = picked === a.id;
          return (
            <button
              key={a.id}
              onClick={() => setPicked(on ? null : a.id)}
              className={cn(
                "flex items-center gap-2 text-left px-3 py-2.5 rounded-[10px] cursor-pointer",
                "border font-sans transition-colors duration-[120ms]",
                on
                  ? "bg-bg border-border-strong"
                  : "bg-surface border-border hover:border-border-strong",
              )}
            >
              <span className="w-[26px] h-[26px] rounded-[7px] shrink-0 bg-surface-2 flex items-center justify-center text-text-2">
                <a.Icon size={13} strokeWidth={1.5} />
              </span>
              <span className="text-[12px] font-medium text-text leading-[1.3]">
                {a.label}
              </span>
            </button>
          );
        })}
      </div>

      {pickedAction && (
        <div className="mt-3 px-3.5 py-3 bg-bg border border-border rounded-[10px] flex flex-col gap-2">
          <p className="text-[13px] text-text leading-[1.6] m-0">
            {pickedAction.answer}
          </p>
          <div className="flex justify-between items-center">
            <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3">
              instant · 0 reasoning tokens
            </span>
            <button
              onClick={() => {
                onSend(pickedAction.label);
                onClose();
              }}
              className="text-[11px] text-accent font-medium flex items-center gap-1 bg-transparent border-0 cursor-pointer"
            >
              Ask in chat <Sparkles size={11} strokeWidth={1.5} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function ActivityDrawer({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-[60] flex justify-end">
      {/* Scrim */}
      <div
        onClick={onClose}
        className="absolute inset-0"
        style={{ background: "rgba(16,24,40,0.28)" }}
        aria-hidden="true"
      />
      {/* Panel */}
      <div className="relative w-[380px] max-w-[92vw] h-full bg-surface border-l border-border shadow-lg flex flex-col">
        <div className="px-5 py-[18px] border-b border-border flex items-center justify-between">
          <div>
            <h3 className="text-[14px] font-semibold text-text m-0">
              Recent activity
            </h3>
            <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3">
              Last 6h · live
            </span>
          </div>
          <button
            onClick={onClose}
            aria-label="Close activity drawer"
            className="text-text-3 hover:text-text p-1"
          >
            <X size={18} strokeWidth={1.5} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-2">
          <ul className="list-none m-0 p-0 flex flex-col">
            {RECENT_ACTIVITY.map((item, i) => (
              <li
                key={i}
                className={cn(
                  "flex items-start gap-2.5 py-2.5",
                  i < RECENT_ACTIVITY.length - 1
                    ? "border-b border-dashed border-border"
                    : "",
                )}
              >
                <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3 w-14 shrink-0 pt-[2px]">
                  {item.time}
                </span>
                <span
                  className={cn(
                    "w-1.5 h-1.5 rounded-full mt-[6px] shrink-0",
                    DOT_COLOR[item.kind],
                  )}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-[12px] text-text leading-[1.45] m-0">
                    {item.what}
                  </p>
                  <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3">
                    {item.who}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="px-5 py-3.5 border-t border-border">
          <Button
            variant="secondary"
            icon={BookOpen}
            className="w-full justify-center"
          >
            Open full audit log
          </Button>
        </div>
      </div>
    </div>
  );
}

function ComposerArea({ onSend }: { onSend: (text: string) => void }) {
  const [draft, setDraft] = useState("");
  const [showActions, setShowActions] = useState(false);

  function submit(text?: string) {
    const msg = (text ?? draft).trim();
    if (!msg) return;
    onSend(msg);
    setDraft("");
    setShowActions(false);
  }

  return (
    <div
      className="sticky bottom-0 z-[5] px-7 pb-6 pt-[14px]"
      style={{
        background:
          "linear-gradient(180deg, rgba(244,241,235,0) 0%, #f4f1eb 36%)",
      }}
    >
      {showActions && (
        <QuickActionsTray
          onSend={submit}
          onClose={() => setShowActions(false)}
        />
      )}

      <div className="flex gap-2.5 items-end">
        {/* Quick actions toggle button */}
        <button
          onClick={() => setShowActions((v) => !v)}
          aria-label="Quick actions"
          aria-pressed={showActions}
          className={cn(
            "shrink-0 h-[50px] px-4 rounded-[14px] cursor-pointer whitespace-nowrap",
            "inline-flex items-center gap-2 font-sans text-[13px] font-medium border",
            "transition-colors duration-[120ms]",
            showActions
              ? "bg-graphite text-white border-graphite"
              : "bg-surface text-text border-border hover:border-border-strong",
          )}
        >
          <Zap
            size={16}
            strokeWidth={1.5}
            className={showActions ? "text-white" : "text-graphite"}
          />
          Quick actions
          <X
            size={13}
            strokeWidth={1.5}
            className={cn(
              showActions ? "text-white" : "text-text-3",
              showActions ? "block" : "hidden",
            )}
          />
        </button>

        {/* Espresso composer pill */}
        <div className="flex-1 min-w-0 bg-accent border border-accent-2 rounded-panel px-3.5 py-3 flex items-center gap-3">
          <span
            className="w-[9px] h-[9px] rounded-full bg-green shrink-0"
            style={{ boxShadow: "0 0 8px rgba(6,118,71,0.6)" }}
          />
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") submit();
            }}
            placeholder='Ask anything, or run an action — "add a property", "draft the weekly energy report"…'
            aria-label="Message Alphacon AI"
            className="flex-1 bg-transparent border-none outline-none font-sans text-[14px] min-w-0 composer-input"
            style={{ color: "#ffffff", caretColor: "#ffffff" }}
          />
          <style>{`.composer-input::placeholder{color:#ffffff;opacity:1;}`}</style>
          <button
            onClick={() => submit()}
            aria-label="Send message"
            className="w-[30px] h-[30px] rounded-[8px] flex items-center justify-center border-0 cursor-pointer shrink-0 font-bold text-[14px]"
            style={{ background: "#fbf3e4", color: "#5e3c1a" }}
          >
            →
          </button>
        </div>
      </div>

      <div className="flex justify-between mt-2 px-0.5">
        <span className="text-[11px] text-text-3">
          Operator persona · asks before any action that changes device state
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-text-3">
          ⌘ K to focus · ⏎ to send
        </span>
      </div>
    </div>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

export function IntelligenceWorkspace() {
  const chat = useChatManager();
  const [showActivity, setShowActivity] = useState(false);
  const { demoMode, toggleDemoMode } = useDemoMode();

  const hasMessages = chat.activeChat.messages.length > 0;

  return (
    <div className="min-h-full flex flex-col">
      <div className="flex items-center justify-between px-7 py-3 border-b border-border bg-surface">
        <div>
          <h2 className="text-[13px] font-semibold text-text">Intelligence</h2>
          <p className="text-[11px] text-text-3">
            {demoMode
              ? "Demo mode: Showing fixture data"
              : "Fresh mode: No mock data"}
          </p>
        </div>
        <Button
          variant={demoMode ? "primary" : "secondary"}
          size="sm"
          onClick={() => toggleDemoMode()}
        >
          {demoMode ? "Demo Mode ON" : "Demo Mode OFF"}
        </Button>
      </div>

      <TabsBar
        chats={chat.chats}
        activeId={chat.activeId}
        onSelect={chat.setActiveId}
        onClose={chat.closeTab}
        onNew={chat.newChat}
        onActivity={() => setShowActivity(true)}
      />

      {hasMessages ? (
        <Transcript messages={chat.activeChat.messages} />
      ) : (
        <EmptyState />
      )}

      <ComposerArea onSend={chat.send} />

      {showActivity && (
        <ActivityDrawer onClose={() => setShowActivity(false)} />
      )}
    </div>
  );
}
