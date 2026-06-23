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
