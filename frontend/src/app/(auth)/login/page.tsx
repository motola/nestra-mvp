"use client"; // Client: react-hook-form + mutation

import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useLogin } from "@/lib/api/hooks/use-auth";
import { useDemoMode } from "@/lib/use-demo-mode";
import { Button } from "@/components/ui/button";
import { Tag } from "@/components/ui/tag";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

type FormValues = z.infer<typeof schema>;

const DEMO_CREDENTIALS = {
  email: "marcus@northernportfolio.co.uk",
  password: "demo-password-123",
};

export default function LoginPage() {
  const login = useLogin();
  const { demoMode } = useDemoMode();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: demoMode ? DEMO_CREDENTIALS : undefined,
  });

  const onSubmit = (values: FormValues) => login.mutate(values);

  return (
    <>
      <div className="flex items-center justify-between mb-1">
        <h1 className="font-serif text-[26px] leading-[1.2] text-text m-0">
          Sign in
        </h1>
        {demoMode && (
          <Tag variant="ok" withDot>
            Demo Mode
          </Tag>
        )}
      </div>
      <p className="text-[13px] text-text-3 mb-6 m-0">
        Welcome back to your portfolio console.
      </p>

      {demoMode && (
        <div className="bg-green-bg border border-green rounded-[9px] px-3 py-2 mb-4">
          <p className="text-[12px] text-green m-0">
            <strong>Demo credentials:</strong> Use the pre-filled email &
            password below
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-[12px] font-medium text-text">
            Email address
          </label>
          <input
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent"
            {...register("email")}
          />
          {errors.email && (
            <p className="text-[11px] text-red m-0">{errors.email.message}</p>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-[12px] font-medium text-text">Password</label>
          <input
            type="password"
            autoComplete="current-password"
            placeholder="••••••••"
            className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent"
            {...register("password")}
          />
          {errors.password && (
            <p className="text-[11px] text-red m-0">
              {errors.password.message}
            </p>
          )}
        </div>

        {login.error && (
          <p className="text-[12px] text-red bg-red-bg rounded-[9px] px-3 py-2 m-0">
            {login.error.message}
          </p>
        )}

        <Button
          variant="primary"
          type="submit"
          disabled={isSubmitting || login.isPending}
          className="w-full justify-center"
        >
          {login.isPending ? "Signing in…" : "Sign in"}
        </Button>
      </form>

      <p className="text-[12px] text-text-3 text-center mt-5 m-0">
        No account?{" "}
        <Link
          href="/signup"
          className="text-accent font-medium no-underline hover:underline"
        >
          Create one
        </Link>
      </p>
    </>
  );
}
