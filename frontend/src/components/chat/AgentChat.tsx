"use client";

import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send } from "lucide-react";
import { streamChat } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";
import { cn } from "@/lib/utils";

const SUGGESTED_PROMPTS = [
  "Which properties have active alerts?",
  "What's the highest energy consuming device?",
  "Are any doors unlocked right now?",
  "Summarise my portfolio status",
];

export function AgentChat() {
  const [open, setOpen] = useState(false);
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, streamingText]);

  async function send(message: string) {
    if (!message.trim() || streaming) return;
    const userMsg: ChatMessage = { role: "user", content: message };
    setHistory((h) => [...h, userMsg]);
    setDraft("");
    setStreaming(true);
    setStreamingText("");

    let accumulated = "";
    await streamChat(message, history, (event) => {
      if (event.type === "text" && event.text) {
        accumulated += event.text;
        setStreamingText(accumulated);
      }
    });

    if (accumulated) {
      setHistory((h) => [...h, { role: "assistant", content: accumulated }]);
    }
    setStreamingText("");
    setStreaming(false);
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(draft);
    }
  }

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen((o) => !o)}
        className={cn(
          "fixed bottom-6 right-6 z-50 w-[52px] h-[52px] rounded-full flex items-center justify-center transition-all",
          "bg-graphite hover:bg-graphite-2 text-surface",
        )}
        aria-label="Open AI assistant"
      >
        {open ? <X size={18} /> : <MessageCircle size={18} />}
      </button>

      {/* Chat panel */}
      {open && (
        <div className="fixed bottom-[72px] right-6 z-50 w-[380px] h-[520px] flex flex-col bg-surface border border-border rounded-2xl overflow-hidden">
          {/* Header */}
          <div className="px-4 py-3 border-b border-border flex items-center justify-between">
            <div>
              <p className="font-body font-normal text-sm text-text">Nestra AI</p>
              <p className="font-body font-light text-xs text-text-3">Portfolio assistant</p>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-text-3 hover:text-text-2 transition-colors"
            >
              <X size={15} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-[200px]">
            {history.length === 0 && !streaming && (
              <div className="space-y-2">
                <p className="font-body font-light text-xs text-text-3 text-center mb-4">
                  Ask me anything about your portfolio
                </p>
                {SUGGESTED_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => send(prompt)}
                    className="w-full text-left px-3 py-2 rounded-lg bg-surface-2 border border-border text-xs font-body font-light text-text-2 hover:border-border-strong hover:text-text transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            )}

            {history.map((msg, i) => (
              <div
                key={i}
                className={cn(
                  "flex",
                  msg.role === "user" ? "justify-end" : "justify-start",
                )}
              >
                <div
                  className={cn(
                    "max-w-[85%] px-3 py-2 rounded-xl text-sm font-body font-light leading-relaxed",
                    msg.role === "user"
                      ? "bg-graphite text-surface rounded-br-sm"
                      : "bg-surface-2 text-text rounded-bl-sm border border-border",
                  )}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {streaming && streamingText && (
              <div className="flex justify-start">
                <div className="max-w-[85%] px-3 py-2 rounded-xl rounded-bl-sm bg-surface-2 border border-border text-sm font-body font-light text-text leading-relaxed">
                  {streamingText}
                  <span className="inline-block w-1 h-3 ml-0.5 bg-text-3 animate-pulse rounded-sm" />
                </div>
              </div>
            )}

            {streaming && !streamingText && (
              <div className="flex justify-start">
                <div className="px-3 py-3 rounded-xl rounded-bl-sm bg-surface-2 border border-border flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-text-3 animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-text-3 animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-text-3 animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t border-border flex items-center gap-2">
            <input
              ref={inputRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your portfolio…"
              disabled={streaming}
              className="flex-1 bg-surface-2 border border-border rounded-lg px-3 py-2 text-sm font-body font-light text-text placeholder:text-text-3 focus:outline-none focus:border-border-strong disabled:opacity-50"
            />
            <button
              onClick={() => send(draft)}
              disabled={!draft.trim() || streaming}
              className="w-8 h-8 rounded-lg bg-graphite text-surface flex items-center justify-center hover:bg-graphite-2 transition-colors disabled:opacity-40 flex-shrink-0"
            >
              <Send size={14} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
