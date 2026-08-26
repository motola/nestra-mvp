"use client"; // Client: chat tabs, messages, composer, quick-actions tray, activity slide-over

import { useState, useEffect } from "react";
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

function uid(prefix: string): string {
  return `${prefix}${Math.random().toString(36).slice(2, 9)}`;
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

    const aiMessageId = uid("m");
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
            { id: aiMessageId, role: "ai" as Role, text: "Thinking..." },
          ],
        };
      }),
    );

    // Call backend API
    const controller = new AbortController();
    (async () => {
      try {
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiUrl}/intelligence/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          signal: controller.signal,
          body: JSON.stringify({ message: msg }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        // Update with AI response
        setChats((cs) =>
          cs.map((c) => {
            if (c.id !== activeId) return c;
            return {
              ...c,
              messages: c.messages.map((m) =>
                m.id === aiMessageId
                  ? { ...m, text: data.response || "No response" }
                  : m,
              ),
            };
          }),
        );
      } catch (error) {
        // Ignore abort errors (component unmounted)
        if (error instanceof Error && error.name === "AbortError") return;
        console.error("Chat error:", error);
        setChats((cs) =>
          cs.map((c) => {
            if (c.id !== activeId) return c;
            return {
              ...c,
              messages: c.messages.map((m) =>
                m.id === aiMessageId
                  ? { ...m, text: "Error: Could not reach AI service" }
                  : m,
              ),
            };
          }),
        );
      }
    })();
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
  onHistoryClick,
}: {
  chats: Chat[];
  activeId: string;
  onSelect: (id: string) => void;
  onClose: (id: string, e: React.MouseEvent) => void;
  onNew: () => void;
  onHistoryClick: () => void;
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
          <Button
            variant="secondary"
            icon={History}
            size="sm"
            onClick={onHistoryClick}
          >
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
          style={{ fontSize: 32, lineHeight: 1.12, letterSpacing: "-0.01em" }}
        >
          Start a conversation
        </h1>
        <p className="text-[15px] text-text-2 mt-2.5 leading-[1.6] m-0">
          Ask questions about your data, get insights, or request actions.
          I&apos;ll confirm before making changes.
        </p>
      </div>
    </div>
  );
}

function Transcript({ messages }: { messages: Message[] }) {
  return (
    <div className="flex-1 overflow-y-auto px-7 py-6 pb-2">
      <div className="max-w-[760px] mx-auto flex flex-col gap-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={cn(
              "flex gap-3.5 items-start",
              m.role === "you" ? "justify-end" : "justify-start",
            )}
          >
            {m.role === "ai" && (
              <span className="font-mono text-[10px] uppercase tracking-[0.08em] w-7 shrink-0 pt-[2px] text-green">
                AI
              </span>
            )}
            <div
              className={cn(
                "px-4 py-3 rounded-lg max-w-xl",
                m.role === "you"
                  ? "bg-accent text-white"
                  : "bg-surface-2 text-text border border-border",
              )}
            >
              <p className="text-[14px] leading-[1.65] m-0">{m.text}</p>
            </div>
            {m.role === "you" && (
              <span className="font-mono text-[10px] uppercase tracking-[0.08em] w-7 shrink-0 pt-[2px] text-text-3">
                You
              </span>
            )}
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

const PLACEHOLDER_TEXTS = [
  "Ask anything, or run an action",
  "Set goals and create routines",
  "Draft the weekly energy report",
];

function ComposerArea({ onSend }: { onSend: (text: string) => void }) {
  const [draft, setDraft] = useState("");
  const [displayedPlaceholder, setDisplayedPlaceholder] = useState("");
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentText = PLACEHOLDER_TEXTS[placeholderIndex];
    const speed = isDeleting ? 50 : 100;
    const delay = isDeleting ? 50 : 2000;

    let timeout: NodeJS.Timeout;

    if (!isDeleting && charIndex < currentText.length) {
      timeout = setTimeout(() => {
        setDisplayedPlaceholder(currentText.slice(0, charIndex + 1));
        setCharIndex(charIndex + 1);
      }, speed);
    } else if (!isDeleting && charIndex === currentText.length) {
      timeout = setTimeout(() => {
        setIsDeleting(true);
      }, delay);
    } else if (isDeleting && charIndex > 0) {
      timeout = setTimeout(() => {
        setDisplayedPlaceholder(currentText.slice(0, charIndex - 1));
        setCharIndex(charIndex - 1);
      }, speed);
    } else if (isDeleting && charIndex === 0) {
      setIsDeleting(false);
      setPlaceholderIndex((placeholderIndex + 1) % PLACEHOLDER_TEXTS.length);
      setCharIndex(0);
    }

    return () => clearTimeout(timeout);
  }, [charIndex, isDeleting, placeholderIndex]);

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
      <div className="flex gap-2.5 items-end justify-center">
        {/* Espresso composer pill */}
        <div className="w-[65%] max-w-2xl bg-accent border border-accent-2 rounded-panel px-3.5 py-3.5 flex items-center gap-3">
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
            placeholder={displayedPlaceholder}
            aria-label="Message Alphacon AI"
            className="flex-1 bg-transparent border-none outline-none font-sans text-[14px] min-w-0 composer-input"
            style={{ color: "#ffffff", caretColor: "#ffffff" }}
          />
          <style>{`.composer-input::placeholder{color:#ffffff;opacity:0.8;}`}</style>
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
    </div>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

function HistoryPanel({
  chats,
  activeId,
  onSelect,
  onClose,
}: {
  chats: Chat[];
  activeId: string;
  onSelect: (id: string) => void;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-start">
      <div className="w-80 bg-surface h-full shadow-lg border-r border-border flex flex-col">
        <div className="px-4 py-3 border-b border-border flex items-center justify-between">
          <h2 className="text-[14px] font-semibold text-text">Chat History</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-surface-2 rounded transition-colors"
            aria-label="Close history"
          >
            <X size={18} className="text-text-2" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {chats.length === 0 ? (
            <div className="px-4 py-6 text-center">
              <p className="text-[12px] text-text-3">No chat history</p>
            </div>
          ) : (
            <div className="space-y-1 p-2">
              {chats.map((chat) => (
                <button
                  key={chat.id}
                  onClick={() => {
                    onSelect(chat.id);
                    onClose();
                  }}
                  className={`w-full text-left px-3 py-2 rounded-[8px] text-[13px] truncate transition-colors ${
                    activeId === chat.id
                      ? "bg-accent text-white"
                      : "text-text hover:bg-bg"
                  }`}
                >
                  {chat.title}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function IntelligenceWorkspace() {
  const chat = useChatManager();
  const [showHistory, setShowHistory] = useState(false);

  const hasMessages = chat.activeChat.messages.length > 0;

  return (
    <div className="min-h-full flex flex-col">
      <TabsBar
        chats={chat.chats}
        activeId={chat.activeId}
        onSelect={chat.setActiveId}
        onClose={chat.closeTab}
        onNew={chat.newChat}
        onHistoryClick={() => setShowHistory(true)}
      />

      {hasMessages ? (
        <Transcript messages={chat.activeChat.messages} />
      ) : (
        <EmptyState />
      )}

      <ComposerArea onSend={chat.send} />

      {showHistory && (
        <HistoryPanel
          chats={chat.chats}
          activeId={chat.activeId}
          onSelect={chat.setActiveId}
          onClose={() => setShowHistory(false)}
        />
      )}
    </div>
  );
}
