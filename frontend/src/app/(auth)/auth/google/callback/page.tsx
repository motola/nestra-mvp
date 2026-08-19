"use client";

import { Suspense, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { useGoogleOAuthCallback } from "@/lib/api/hooks/use-auth";

function GoogleCallbackForm() {
  const searchParams = useSearchParams();
  const googleCallback = useGoogleOAuthCallback();

  useEffect(() => {
    const code = searchParams.get("code");
    const error = searchParams.get("error");

    console.log(
      "Google callback - code:",
      code ? "present" : "missing",
      "error:",
      error,
    );

    if (error) {
      console.error("Google OAuth error from provider:", error);
      return;
    }

    if (code) {
      console.log("Exchanging code for token...");
      googleCallback.mutate({ code });
    }
  }, [searchParams, googleCallback]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <div className="animate-spin">
        <div className="h-8 w-8 border-4 border-accent border-t-transparent rounded-full"></div>
      </div>
      <p className="text-[14px] text-text">Signing in with Google...</p>
      {googleCallback.isPending && (
        <p className="text-[12px] text-text-3">
          Exchanging authorization code...
        </p>
      )}
      {googleCallback.error && (
        <div className="text-center">
          <p className="text-[12px] text-red mb-2">
            Error: {googleCallback.error.message}
          </p>
          <p className="text-[11px] text-text-3">Please try signing in again</p>
        </div>
      )}
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <GoogleCallbackForm />
    </Suspense>
  );
}
