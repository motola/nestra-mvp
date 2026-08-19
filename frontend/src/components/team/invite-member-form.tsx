"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

type Role = "admin" | "manager" | "viewer";

interface InviteMemberFormProps {
  onClose: () => void;
  onSubmit: (data: { email: string; role: Role }) => void;
}

const ROLES: { id: Role; label: string; description: string }[] = [
  {
    id: "admin",
    label: "Admin",
    description: "Full access to all settings and members",
  },
  {
    id: "manager",
    label: "Manager",
    description: "Manage portfolios, properties, and integrations",
  },
  {
    id: "viewer",
    label: "Viewer",
    description: "Read-only access to portfolios and properties",
  },
];

export function InviteMemberForm({ onClose, onSubmit }: InviteMemberFormProps) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<Role>("manager");
  const [error, setError] = useState("");

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email.trim()) {
      setError("Email is required");
      return;
    }

    if (!validateEmail(email)) {
      setError("Please enter a valid email address");
      return;
    }

    onSubmit({ email, role });
    setEmail("");
    setRole("manager");
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-surface rounded-panel p-6 w-full max-w-md shadow-lg">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-[20px] font-serif text-text m-0">
            Invite Team Member
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-surface-2 rounded transition-colors"
          >
            <X size={18} className="text-text-2" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Email */}
          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-1.5">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="member@company.com"
              className={cn(
                "w-full px-3 py-2.5 rounded-[8px] border bg-bg text-text text-[14px]",
                "placeholder:text-text-3 transition-colors",
                error ? "border-red" : "border-border focus:border-text",
              )}
            />
            {error && <p className="text-[12px] text-red mt-1">{error}</p>}
          </div>

          {/* Role Selection */}
          <div>
            <label className="block text-[12px] font-semibold text-text-2 uppercase tracking-[0.08em] mb-2.5">
              Assign Role
            </label>
            <div className="flex flex-col gap-2">
              {ROLES.map((r) => (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => setRole(r.id)}
                  className={cn(
                    "p-3 rounded-[8px] border text-left transition-colors",
                    role === r.id
                      ? "bg-graphite border-graphite"
                      : "bg-surface-2 border-border hover:border-border-strong",
                  )}
                >
                  <div className="flex items-center gap-2">
                    <div
                      className={cn(
                        "w-4 h-4 rounded border",
                        role === r.id ? "bg-text border-text" : "border-border",
                      )}
                    />
                    <div>
                      <p
                        className={cn(
                          "text-[13px] font-semibold m-0",
                          role === r.id ? "text-white" : "text-text",
                        )}
                      >
                        {r.label}
                      </p>
                      <p
                        className={cn(
                          "text-[12px] m-0 mt-0.5",
                          role === r.id ? "text-white/70" : "text-text-3",
                        )}
                      >
                        {r.description}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 mt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" className="flex-1">
              Send Invite
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
