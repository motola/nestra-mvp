"use client"; // Client: react-hook-form + mutation

import Link from "next/link";
import { useState, Suspense } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  useSignup,
  useGoogleOAuthUrl,
  useCheckEmailAvailability,
} from "@/lib/api/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { isPublicMailDomain, extractOrgNameFromEmail } from "@/lib/utils/email";

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

function SignupForm() {
  const signup = useSignup();
  const googleOAuthUrl = useGoogleOAuthUrl();
  const checkEmail = useCheckEmailAvailability();
  const [showOrgModal, setShowOrgModal] = useState(false);
  const [pendingOrgName, setPendingOrgName] = useState("");
  const [emailError, setEmailError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const email = watch("email");

  const handleGoogleSignup = async () => {
    if (!email) {
      alert("Please enter your email first");
      return;
    }

    // Check email availability first
    setEmailError("");
    try {
      const result = await checkEmail.mutateAsync({ email });
      if (!result.available) {
        setEmailError(result.message);
        return;
      }
    } catch {
      setEmailError("Failed to check email availability");
      return;
    }

    // If public mail domain, ask for org name first
    if (isPublicMailDomain(email)) {
      setShowOrgModal(true);
    } else {
      // Auto-detect org name from domain
      const autoOrgName = extractOrgNameFromEmail(email);
      if (googleOAuthUrl.data?.url) {
        // Store email and org name for backend
        sessionStorage.setItem("signup_email", email);
        sessionStorage.setItem("signup_org_name", autoOrgName);
        window.location.href = googleOAuthUrl.data.url;
      }
    }
  };

  const handleOrgNameSubmit = (orgName: string) => {
    if (!orgName.trim()) {
      alert("Please enter an organization name");
      return;
    }
    if (googleOAuthUrl.data?.url) {
      // Store email and org name for backend
      sessionStorage.setItem("signup_email", email);
      sessionStorage.setItem("signup_org_name", orgName);
      window.location.href = googleOAuthUrl.data.url;
    }
    setShowOrgModal(false);
  };

  const onSubmit = (values: FormValues) => signup.mutate(values);

  return (
    <>
      <h1 className="font-serif text-[26px] leading-[1.2] text-text m-0 mb-1">
        Create your account
      </h1>
      <p className="text-[13px] text-text-3 mb-6 m-0">
        Set up your organisation and start managing your portfolio.
      </p>

      {/* Google Signup Button */}
      <Button
        variant="secondary"
        type="button"
        onClick={handleGoogleSignup}
        disabled={googleOAuthUrl.isPending || checkEmail.isPending}
        className="w-full justify-center gap-2 mb-4"
      >
        <svg
          className="w-5 h-5"
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
        Sign up with Google
      </Button>

      {emailError && (
        <p className="text-[12px] text-red bg-red-bg rounded-[9px] px-3 py-2 m-0 mb-4">
          {emailError}
        </p>
      )}

      <div className="relative my-4">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border"></div>
        </div>
        <div className="relative flex justify-center text-[12px]">
          <span className="px-2 bg-surface text-text-3">
            Or continue with email
          </span>
        </div>
      </div>

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

      {/* Organization Name Modal */}
      {showOrgModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-surface border border-border rounded-card p-6 max-w-sm w-full">
            <h2 className="font-serif text-[20px] text-text m-0 mb-2">
              Organisation Name
            </h2>
            <p className="text-[12px] text-text-3 mb-4">
              What&apos;s your organisation name? (Can be changed later in
              settings)
            </p>
            <input
              autoFocus
              type="text"
              placeholder="Your Organisation"
              value={pendingOrgName}
              onChange={(e) => setPendingOrgName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleOrgNameSubmit(pendingOrgName);
                }
              }}
              className="w-full bg-bg border border-border rounded-[9px] px-3 py-2 text-[13px] text-text outline-none focus:border-accent mb-4"
            />
            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={() => setShowOrgModal(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={() => handleOrgNameSubmit(pendingOrgName)}
                className="flex-1"
              >
                Continue
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default function SignupPage() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col items-center justify-center min-h-screen">
          <div className="max-w-[420px] w-full bg-surface border border-border rounded-card p-8">
            <div className="h-20 bg-gray-200 rounded animate-pulse mb-4" />
            <div className="h-10 bg-gray-200 rounded animate-pulse" />
          </div>
        </div>
      }
    >
      <SignupForm />
    </Suspense>
  );
}
