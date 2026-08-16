"use client"; // Client: react-hook-form + mutation

import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useForgotPassword } from "@/lib/api/hooks/use-auth";
import { Button } from "@/components/ui/button";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
});

type FormValues = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const forgotPassword = useForgotPassword();
  const [submitted, setSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = (values: FormValues) => {
    forgotPassword.mutate(values, {
      onSuccess: () => {
        setSubmitted(true);
      },
    });
  };

  if (submitted) {
    return (
      <>
        <h1 className="font-serif text-[26px] leading-[1.2] text-text m-0 mb-1">
          Check your email
        </h1>
        <p className="text-[13px] text-text-3 mb-6 m-0">
          We&apos;ve sent a password reset link to your email address. Click the
          link to set a new password.
        </p>

        <div className="bg-green-bg border border-green rounded-[9px] px-3 py-2 mb-6">
          <p className="text-[12px] text-green m-0">
            <strong>Check your inbox</strong> — if you don&apos;t see it in a
            few minutes, check your spam folder.
          </p>
        </div>

        <Link href="/login">
          <Button variant="primary" className="w-full justify-center">
            Back to sign in
          </Button>
        </Link>
      </>
    );
  }

  return (
    <>
      <h1 className="font-serif text-[26px] leading-[1.2] text-text m-0 mb-1">
        Reset your password
      </h1>
      <p className="text-[13px] text-text-3 mb-6 m-0">
        Enter your email address and we&apos;ll send you a link to reset your
        password.
      </p>

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

        {forgotPassword.error && (
          <p className="text-[12px] text-red bg-red-bg rounded-[9px] px-3 py-2 m-0">
            {forgotPassword.error.message}
          </p>
        )}

        <Button
          variant="primary"
          type="submit"
          disabled={isSubmitting || forgotPassword.isPending}
          className="w-full justify-center"
        >
          {forgotPassword.isPending ? "Sending…" : "Send reset link"}
        </Button>
      </form>

      <p className="text-[12px] text-text-3 text-center mt-5 m-0">
        Remember your password?{" "}
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
