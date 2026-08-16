"use client"; // Client: auto-verify with token

import { useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { useVerifyEmail } from "@/lib/api/hooks/use-auth";

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const verifyEmail = useVerifyEmail();

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

          <p className="text-[12px] text-text-3 text-center m-0">
            Please try signing up again or contact support if you need help.
          </p>
        </>
      )}

      {!token && !verifyEmail.isPending && (
        <>
          <div className="bg-red-bg border border-red rounded-[9px] px-3 py-2 mb-6">
            <p className="text-[12px] text-red m-0">
              <strong>Invalid verification link</strong> — no token provided.
            </p>
          </div>

          <p className="text-[12px] text-text-3 text-center m-0">
            Please check the link in your email or request a new one.
          </p>
        </>
      )}
    </>
  );
}
