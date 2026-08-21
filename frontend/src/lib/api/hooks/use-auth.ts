import { useQuery, useMutation } from "@tanstack/react-query";
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

interface ForgotPasswordResponse {
  message: string;
  account_exists: boolean;
}

export function useForgotPassword() {
  return useMutation<ForgotPasswordResponse, ApiError, ForgotPasswordPayload>({
    mutationFn: (payload) =>
      apiFetch<ForgotPasswordResponse>("/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  });
}

// ─── Reset Password ───────────────────────────────────────────────────────────

interface ResetPasswordPayload {
  token: string;
  new_password: string;
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
      router.push("/login");
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

// ─── Logout ───────────────────────────────────────────────────────────────────

export function useLogout() {
  const { clearSession } = useAuth();
  const router = useRouter();

  return useMutation<void, ApiError, void>({
    mutationFn: () =>
      apiFetch<void>("/auth/logout", {
        method: "POST",
      }),
    onSuccess: () => {
      clearSession();
      router.push("/login");
    },
    onError: () => {
      clearSession();
      router.push("/login");
    },
  });
}

// ─── Google OAuth ─────────────────────────────────────────────────────────────

interface GoogleOAuthUrlResponse {
  url: string;
}

interface GoogleOAuthCallbackPayload {
  code: string;
}

export function useGoogleOAuthUrl() {
  return useQuery<GoogleOAuthUrlResponse, ApiError>({
    queryKey: ["google-oauth-url"],
    queryFn: () =>
      apiFetch<GoogleOAuthUrlResponse>("/auth/google/url", {
        method: "GET",
      }),
    enabled: typeof window !== "undefined",
    retry: false,
    throwOnError: false,
  });
}

export function useGoogleOAuthCallback() {
  const { setSession } = useAuth();
  const router = useRouter();

  return useMutation<TokenResponse, ApiError, GoogleOAuthCallbackPayload>({
    mutationFn: (payload) => {
      // Include signup email and org_name from sessionStorage if available
      const signupEmail = sessionStorage.getItem("signup_email");
      const orgName = sessionStorage.getItem("signup_org_name");
      sessionStorage.removeItem("signup_email");
      sessionStorage.removeItem("signup_org_name");
      return apiFetch<TokenResponse>("/auth/google/callback", {
        method: "POST",
        body: JSON.stringify({
          ...payload,
          ...(signupEmail && { signup_email: signupEmail }),
          ...(orgName && { org_name: orgName }),
        }),
      });
    },
    onSuccess: async ({ access_token }) => {
      setSession(access_token);
      // Wait a brief moment for session to be stored
      await new Promise((resolve) => setTimeout(resolve, 100));
      router.push("/intelligence");
    },
    onError: (error) => {
      console.error("Google OAuth callback error:", error);
    },
  });
}

// ─── Microsoft OAuth ──────────────────────────────────────────────────────────

interface MicrosoftOAuthUrlResponse {
  url: string;
}

interface MicrosoftOAuthCallbackPayload {
  code: string;
}

export function useMicrosoftOAuthUrl() {
  return useQuery<MicrosoftOAuthUrlResponse, ApiError>({
    queryKey: ["microsoft-oauth-url"],
    queryFn: () =>
      apiFetch<MicrosoftOAuthUrlResponse>("/auth/microsoft/url", {
        method: "GET",
      }),
    enabled: false,
    retry: false,
  });
}

export function useMicrosoftOAuthCallback() {
  const { setSession } = useAuth();
  const router = useRouter();

  return useMutation<TokenResponse, ApiError, MicrosoftOAuthCallbackPayload>({
    mutationFn: (payload) => {
      // Include signup email and org_name from sessionStorage if available
      const signupEmail = sessionStorage.getItem("signup_email");
      const orgName = sessionStorage.getItem("signup_org_name");
      sessionStorage.removeItem("signup_email");
      sessionStorage.removeItem("signup_org_name");
      return apiFetch<TokenResponse>("/auth/microsoft/callback", {
        method: "POST",
        body: JSON.stringify({
          ...payload,
          ...(signupEmail && { signup_email: signupEmail }),
          ...(orgName && { org_name: orgName }),
        }),
      });
    },
    onSuccess: async ({ access_token }) => {
      setSession(access_token);
      // Wait a brief moment for session to be stored
      await new Promise((resolve) => setTimeout(resolve, 100));
      router.push("/intelligence");
    },
    onError: (error) => {
      console.error("Microsoft OAuth callback error:", error);
    },
  });
}
