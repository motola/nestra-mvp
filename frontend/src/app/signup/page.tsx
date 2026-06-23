"use client";

// Client: interactive sign-up form.

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { useAuth } from "@/contexts/AuthContext";

export default function SignupPage() {
  const router = useRouter();
  const { signup } = useAuth();
  const [fullName, setFullName] = useState("");
  const [organization, setOrganization] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await signup({
        email,
        password,
        full_name: fullName,
        organization_name: organization || undefined,
      });
      router.push("/dashboard");
    } catch (err) {
      const message =
        err instanceof Error && err.message.includes("409")
          ? "That email is already registered."
          : "Could not create your account. Please try again.";
      setError(message);
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-2 px-4 py-10">
      <div className="w-full max-w-[420px] bg-surface border border-border rounded-xl p-8">
        <p className="font-display text-3xl text-text mb-1">Nestra</p>
        <h1 className="font-body text-text-2 text-sm mb-6">
          Create your account
        </h1>

        <form onSubmit={onSubmit} className="flex flex-col gap-4">
          <Field
            label="Full name"
            value={fullName}
            onChange={setFullName}
            type="text"
          />
          <Field
            label="Organisation"
            value={organization}
            onChange={setOrganization}
            type="text"
            optional
          />
          <Field label="Email" value={email} onChange={setEmail} type="email" />
          <Field
            label="Password"
            value={password}
            onChange={setPassword}
            type="password"
          />

          {error && <p className="text-red text-sm">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="bg-graphite text-surface rounded-lg px-4 py-2.5 font-medium hover:bg-graphite-2 disabled:opacity-60"
          >
            {submitting ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="text-text-3 text-sm mt-6">
          Already have an account?{" "}
          <Link
            href="/login"
            className="text-text underline underline-offset-2"
          >
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type,
  optional,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type: string;
  optional?: boolean;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="font-mono text-xs uppercase tracking-widest text-text-3">
        {label}
      </span>
      <input
        type={type}
        required={!optional}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="bg-bg border border-border rounded-lg px-3 py-2 text-text outline-none focus:border-border-strong"
      />
    </label>
  );
}
