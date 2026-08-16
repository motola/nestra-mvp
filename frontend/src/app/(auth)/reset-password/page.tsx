"use client"; // Client: react-hook-form + mutation

import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useResetPassword } from "@/lib/api/hooks/use-auth";
import { Button } from "@/components/ui/button";

const schema = z
  .object({
    password: z.string().min(8, "Password must be at least 8 characters"),
    password_confirm: z
      .string()
      .min(8, "Password must be at least 8 characters"),
  })
  .refine((data) => data.password === data.password_confirm, {
    message: "Passwords don't match",
    path: ["password_confirm"],
  });

type FormValues = z.infer<typeof schema>;

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const resetPassword = useResetPassword();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = (values: FormValues) => {
    if (!token) {
      return;
    }

    resetPassword.mutate({
      token,
      password: values.password,
      password_confirm: values.password_confirm,
    });
  };

  if (!token) {
    return (
      <>
        <h1 className="font-serif text-[26px] leading-[1.2] text-text m-0 mb-1">
          Invalid reset link
        </h1>
        <p className="text-[13px] text-text-3 mb-6 m-0">
          The password reset link is missing or invalid. Please request a new
          one.
        </p>

        <div className="bg-red-bg border border-red rounded-[9px] px-3 py-2 mb-6">
          <p className="text-[12px] text-red m-0">
            <strong>No reset token found</strong> — this link may have expired.
          </p>
        </div>

        <a href="/forgot-password">
          <Button variant="primary" className="w-full justify-center">
            Request new reset link
          </Button>
        </a>
      </>
    );
  }

  return (
    <>
      <h1 className="font-serif text-[26px] leading-[1.2] text-text m-0 mb-1">
        Set a new password
      </h1>
      <p className="text-[13px] text-text-3 mb-6 m-0">
        Enter a new password to regain access to your account.
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-[12px] font-medium text-text">Password</label>
          <input
            type="password"
            autoComplete="new-password"
            placeholder="Min. 8 characters"
            className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent"
            {...register("password")}
          />
          {errors.password && (
            <p className="text-[11px] text-red m-0">
              {errors.password.message}
            </p>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-[12px] font-medium text-text">
            Confirm password
          </label>
          <input
            type="password"
            autoComplete="new-password"
            placeholder="••••••••"
            className="bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent"
            {...register("password_confirm")}
          />
          {errors.password_confirm && (
            <p className="text-[11px] text-red m-0">
              {errors.password_confirm.message}
            </p>
          )}
        </div>

        {resetPassword.error && (
          <p className="text-[12px] text-red bg-red-bg rounded-[9px] px-3 py-2 m-0">
            {resetPassword.error.message}
          </p>
        )}

        <Button
          variant="primary"
          type="submit"
          disabled={isSubmitting || resetPassword.isPending}
          className="w-full justify-center"
        >
          {resetPassword.isPending ? "Resetting…" : "Set new password"}
        </Button>
      </form>
    </>
  );
}
