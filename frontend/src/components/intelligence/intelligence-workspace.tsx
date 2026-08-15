"use client"; // Client: chat tabs, messages, composer, quick-actions tray, activity slide-over

import { useState } from "react";
import { X, Plus, Sparkles, History } from "lucide-react";
import { cn } from "@/lib/cn";
import { Button } from "@/components/ui/button";

// ─── Types ────────────────────────────────────────────────────────────────────

type Role = "you" | "ai";

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

// ─── Helpers ──────────────────────────────────────────────────────────────────

let _counter = 20;
function uid(prefix: string): string {
  return `${prefix}${_counter++}`;
}

// ─── Chat state hook ──────────────────────────────────────────────────────────

function useChatManager() {
  const empty: Chat = {
    id: "new0",
    title: "New chat",
    when: "now",
    messages: [],
  };
  const [chats, setChats] = useState<Chat[]>([empty]);
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
            { id: uid("m"), role: "ai" as Role, text: "Thinking..." },
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
}: {
  chats: Chat[];
  activeId: string;
  onSelect: (id: string) => void;
  onClose: (id: string, e: React.MouseEvent) => void;
  onNew: () => void;
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
          <Button variant="secondary" icon={History} size="sm">
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
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-7 py-10 text-center gap-4">
      <div className="w-[52px] h-[52px] rounded-[13px] bg-accent flex items-center justify-center">
        <Sparkles size={24} strokeWidth={1.5} color="#ffffff" />
      </div>
      <div className="max-w-[520px]">
        <h1
          className="font-serif text-text m-0"
          style={{ fontSize: 40, lineHeight: 1.12, letterSpacing: "-0.01em" }}
        >
          Start a conversation
        </h1>
        <p className="text-[13px] text-text-2 mt-2.5 leading-[1.6] m-0">
          Ask questions about your data, get insights, or request actions.
          I&apos;ll show what I checked and ask before anything that changes
          state.
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

function ComposerArea({ onSend }: { onSend: (text: string) => void }) {
  const [draft, setDraft] = useState("");

  function submit(text?: string) {
    const msg = (text ?? draft).trim();
    if (!msg) return;
    onSend(msg);
    setDraft("");
  }

  return (
    <div
      className="sticky bottom-0 z-[5] px-7 pb-6 pt-[14px]"
      style={{
        background:
          "linear-gradient(180deg, rgba(244,241,235,0) 0%, #f4f1eb 36%)",
      }}
    >
      <div className="flex gap-2.5 items-end">
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

  const hasMessages = chat.activeChat.messages.length > 0;

  return (
    <div className="min-h-full flex flex-col">
      <div className="flex items-center justify-between px-7 py-3 border-b border-border bg-surface">
        <div>
          <h2 className="text-[13px] font-semibold text-text">Intelligence</h2>
          <p className="text-[11px] text-text-3">Chat with your AI assistant</p>
        </div>
      </div>

      <TabsBar
        chats={chat.chats}
        activeId={chat.activeId}
        onSelect={chat.setActiveId}
        onClose={chat.closeTab}
        onNew={chat.newChat}
      />

      {hasMessages ? (
        <Transcript messages={chat.activeChat.messages} />
      ) : (
        <EmptyState />
      )}

      <ComposerArea onSend={chat.send} />
    </div>
  );
}
