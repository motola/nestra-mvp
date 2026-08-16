import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { apiFetch, ApiError } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/provider";

// ─── Shapes matching backend schemas ─────────────────────────────────────────

interface SignupPayload {
  email: string;
  full_name: string;
  password: string;
  org_name: string;
  legal_name: string;
}

interface LoginPayload {
  email: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  organization_id: string;
}

// ─── Signup ───────────────────────────────────────────────────────────────────

export function useSignup() {
  const { setSession } = useAuth();
  const router = useRouter();

  return useMutation<TokenResponse, ApiError, SignupPayload>({
    mutationFn: (payload) =>
      apiFetch<TokenResponse>("/auth/signup", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: ({ access_token }) => {
      setSession(access_token);
      router.push("/intelligence");
    },
  });
}

// ─── Login ────────────────────────────────────────────────────────────────────

export function useLogin() {
  const { setSession } = useAuth();
  const router = useRouter();

  return useMutation<TokenResponse, ApiError, LoginPayload>({
    mutationFn: (payload) =>
      apiFetch<TokenResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: ({ access_token }) => {
      setSession(access_token);
      router.push("/intelligence");
    },
  });
}

// ─── Forgot Password ──────────────────────────────────────────────────────────

interface ForgotPasswordPayload {
  email: string;
}

interface MessageResponse {
  message: string;
}

export function useForgotPassword() {
  return useMutation<MessageResponse, ApiError, ForgotPasswordPayload>({
    mutationFn: (payload) =>
      apiFetch<MessageResponse>("/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  });
}

// ─── Reset Password ───────────────────────────────────────────────────────────

interface ResetPasswordPayload {
  token: string;
  password: string;
  password_confirm: string;
}

export function useResetPassword() {
  const { setSession } = useAuth();
  const router = useRouter();

  return useMutation<TokenResponse, ApiError, ResetPasswordPayload>({
    mutationFn: (payload) =>
      apiFetch<TokenResponse>("/auth/reset-password", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: ({ access_token }) => {
      setSession(access_token);
      router.push("/overview");
    },
  });
}

// ─── Verify Email ─────────────────────────────────────────────────────────────

interface VerifyEmailPayload {
  token: string;
}

export function useVerifyEmail() {
  const { setSession } = useAuth();
  const router = useRouter();

  return useMutation<TokenResponse, ApiError, VerifyEmailPayload>({
    mutationFn: (payload) =>
      apiFetch<TokenResponse>("/auth/verify-email", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: ({ access_token }) => {
      setSession(access_token);
      router.push("/overview");
    },
  });
}

// ─── Resend Verification Email ────────────────────────────────────────────────

export function useResendVerificationEmail() {
  return useMutation<void, ApiError, VerifyEmailPayload>({
    mutationFn: (payload) =>
      apiFetch<void>("/auth/resend-verification-email", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  });
}
