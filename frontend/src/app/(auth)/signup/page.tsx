"use client"; // Client: react-hook-form + mutation

import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useSignup } from "@/lib/api/hooks/use-auth";
import { Button } from "@/components/ui/button";

const schema = z.object({
  full_name: z.string().min(1, "Full name is required"),
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  org_name: z.string().min(1, "Organisation name is required"),
  legal_name: z.string().min(1, "Legal name is required"),
});

type FormValues = z.infer<typeof schema>;

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-[12px] font-medium text-text">{label}</label>
      {children}
      {error && <p className="text-[11px] text-red m-0">{error}</p>}
    </div>
  );
}

export default function SignupPage() {
  const signup = useSignup();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = (values: FormValues) => signup.mutate(values);

  return (
    <>
      <h1 className="font-serif text-[26px] leading-[1.2] text-text m-0 mb-1">
        Create your account
      </h1>
      <p className="text-[13px] text-text-3 mb-6 m-0">
        Set up your organisation and start managing your portfolio.
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <Field label="Full name" error={errors.full_name?.message}>
          <input
            type="text"
            autoComplete="name"
            placeholder="Marcus Chen"
            className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent"
            {...register("full_name")}
          />
        </Field>

        <Field label="Email address" error={errors.email?.message}>
          <input
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent"
            {...register("email")}
          />
        </Field>

        <Field label="Password" error={errors.password?.message}>
          <input
            type="password"
            autoComplete="new-password"
            placeholder="Min. 8 characters"
            className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent"
            {...register("password")}
          />
        </Field>

        <div className="h-px bg-border" />

        <Field
          label="Organisation display name"
          error={errors.org_name?.message}
        >
          <input
            type="text"
            placeholder="Chen Property Holdings"
            className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent"
            {...register("org_name")}
          />
        </Field>

        <Field label="Legal name" error={errors.legal_name?.message}>
          <input
            type="text"
            placeholder="Chen Holdings Ltd"
            className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent"
            {...register("legal_name")}
          />
        </Field>

        {signup.error && (
          <p className="text-[12px] text-red bg-red-bg rounded-[9px] px-3 py-2 m-0">
            {signup.error.message}
          </p>
        )}

        <Button
          variant="primary"
          type="submit"
          disabled={isSubmitting || signup.isPending}
          className="w-full justify-center"
        >
          {signup.isPending ? "Creating account…" : "Create account"}
        </Button>
      </form>

      <p className="text-[12px] text-text-3 text-center mt-5 m-0">
        Already have an account?{" "}
        <Link
          href="/login"
          className="text-accent font-medium no-underline hover:underline"
        >
          Sign in
        </Link>
      </p>
    </>
  );
}
