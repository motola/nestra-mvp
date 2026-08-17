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

    if (error) {
      console.error("Google OAuth error:", error);
      return;
    }

    if (code) {
      googleCallback.mutate({ code });
    }
  }, [searchParams, googleCallback]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <div className="animate-spin">
        <div className="h-8 w-8 border-4 border-accent border-t-transparent rounded-full"></div>
      </div>
      <p className="text-[14px] text-text">Signing in with Google...</p>
      {googleCallback.error && (
        <p className="text-[12px] text-red">{googleCallback.error.message}</p>
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
