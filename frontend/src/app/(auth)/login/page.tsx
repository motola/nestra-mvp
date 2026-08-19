"use client"; // Client: react-hook-form + mutation

import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  useLogin,
  useGoogleOAuthUrl,
  useMicrosoftOAuthUrl,
} from "@/lib/api/hooks/use-auth";
import { Button } from "@/components/ui/button";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const login = useLogin();
  const googleOAuthUrl = useGoogleOAuthUrl();
  const microsoftOAuthUrl = useMicrosoftOAuthUrl();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (values: FormValues) => login.mutate(values);

  const handleGoogleLogin = async () => {
    if (googleOAuthUrl.data?.url) {
      window.location.href = googleOAuthUrl.data.url;
    }
  };

  const handleMicrosoftLogin = async () => {
    if (microsoftOAuthUrl.data?.url) {
      window.location.href = microsoftOAuthUrl.data.url;
    }
  };

  return (
    <>
      <h1 className="font-serif text-[26px] leading-[1.2] text-text m-0 mb-1">
        Sign in
      </h1>
      <p className="text-[13px] text-text-3 mb-6 m-0">
        Welcome back to your portfolio console.
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

        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <label className="text-[12px] font-medium text-text">
              Password
            </label>
            <Link
              href="/forgot-password"
              className="text-[11px] text-accent font-medium no-underline hover:underline"
            >
              Forgot password?
            </Link>
          </div>
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

      <div className="relative my-5">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border"></div>
        </div>
        <div className="relative flex justify-center text-[12px]">
          <span className="px-2 bg-bg text-text-3">Or continue with</span>
        </div>
      </div>

      <div className="flex gap-3 justify-center">
        <Button
          variant="secondary"
          type="button"
          onClick={handleGoogleLogin}
          disabled={googleOAuthUrl.isPending || googleOAuthUrl.isError}
          className="w-12 h-12 p-0 justify-center items-center"
          title="Sign in with Google"
        >
          <svg
            className="w-6 h-6"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              fill="#4285F4"
            />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#34A853"
            />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              fill="#FBBC05"
            />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              fill="#EA4335"
            />
          </svg>
        </Button>
        <Button
          variant="secondary"
          type="button"
          onClick={handleMicrosoftLogin}
          disabled={microsoftOAuthUrl.isPending || microsoftOAuthUrl.isError}
          className="w-12 h-12 p-0 justify-center items-center opacity-50 cursor-not-allowed"
          title="Microsoft sign in not configured"
        >
          <svg
            className="w-6 h-6"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect x="1" y="1" width="9" height="9" fill="#F25022" />
            <rect x="12" y="1" width="9" height="9" fill="#7FBA00" />
            <rect x="1" y="12" width="9" height="9" fill="#00A4EF" />
            <rect x="12" y="12" width="9" height="9" fill="#FFB900" />
          </svg>
        </Button>
      </div>

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
