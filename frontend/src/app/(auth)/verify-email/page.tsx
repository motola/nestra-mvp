"use client"; // Client: auto-verify with token

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";
import {
  useVerifyEmail,
  useResendVerificationEmail,
} from "@/lib/api/hooks/use-auth";
import { Button } from "@/components/ui/button";

function VerifyEmailForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const verifyEmail = useVerifyEmail();
  const resendEmail = useResendVerificationEmail();
  const [showResent, setShowResent] = useState(false);

  const handleResend = () => {
    if (token) {
      resendEmail.mutate({ token });
      setShowResent(true);
      setTimeout(() => setShowResent(false), 3000);
    }
  };

  useEffect(() => {
    if (token && !verifyEmail.isPending) {
      verifyEmail.mutate({ token });
    }
  }, [token, verifyEmail]);

  return (
    <>
      <h1 className="font-serif text-[26px] leading-[1.2] text-text m-0 mb-1">
        Verifying your email
      </h1>
      <p className="text-[13px] text-text-3 mb-6 m-0">
        One moment while we confirm your email address...
      </p>

      {verifyEmail.isPending && (
        <div className="flex flex-col items-center justify-center gap-4 py-8">
          <div className="w-8 h-8 border-4 border-border border-t-accent rounded-full animate-spin" />
          <p className="text-[13px] text-text-3">Verifying…</p>
        </div>
      )}

      {verifyEmail.error && (
        <>
          <div className="bg-red-bg border border-red rounded-[9px] px-3 py-2 mb-6">
            <p className="text-[12px] text-red m-0">
              <strong>Verification failed</strong> — {verifyEmail.error.message}
            </p>
          </div>

          {token && (
            <>
              <p className="text-[12px] text-text-3 text-center mb-4 m-0">
                Didn&apos;t receive the email or link expired?
              </p>
              <Button
                variant="primary"
                type="button"
                disabled={resendEmail.isPending}
                className="w-full justify-center"
                onClick={handleResend}
              >
                {resendEmail.isPending
                  ? "Sending…"
                  : "Resend verification email"}
              </Button>
            </>
          )}
        </>
      )}

      {!token && !verifyEmail.isPending && (
        <>
          <div className="bg-red-bg border border-red rounded-[9px] px-3 py-2 mb-6">
            <p className="text-[12px] text-red m-0">
              <strong>Missing verification link</strong> — this link may have
              expired.
            </p>
          </div>

          <p className="text-[12px] text-text-3 text-center mb-4 m-0">
            You can request a new verification link from the login page.
          </p>

          <a href="/login">
            <Button variant="primary" className="w-full justify-center">
              Return to login
            </Button>
          </a>
        </>
      )}

      {verifyEmail.isSuccess && (
        <>
          <div className="bg-green-bg border border-green rounded-[9px] px-3 py-2 mb-6">
            <p className="text-[12px] text-green m-0">
              <strong>Email verified!</strong> Your email address has been
              confirmed. You can now sign in.
            </p>
          </div>

          <a href="/login">
            <button className="w-full rounded-[8px] bg-accent px-4 py-2 text-center font-medium text-white hover:bg-accent/90">
              Return to login
            </button>
          </a>
        </>
      )}

      {showResent && (
        <div className="bg-green-bg border border-green rounded-[9px] px-3 py-2 mt-4">
          <p className="text-[12px] text-green m-0">
            ✓ Verification email resent! Check your inbox.
          </p>
        </div>
      )}
    </>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <VerifyEmailForm />
    </Suspense>
  );
}
