"use client"; // Client: holds session state + provides auth context

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { clearToken, getToken, setToken } from "@/lib/auth/session";
import { apiFetch } from "@/lib/api/client";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
}

export interface AuthOrganization {
  id: string;
  name: string;
  slug: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  organization: AuthOrganization | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setSession: (token: string) => void;
  clearSession: () => void;
}

// ─── Context ──────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null);

// ─── Provider ─────────────────────────────────────────────────────────────────

interface MeResponse {
  user: AuthUser;
  organization: AuthOrganization;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [organization, setOrganization] = useState<AuthOrganization | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);

  // Hydrate session from cookie on mount
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setIsLoading(false);
      return;
    }
    // TODO: Once Authorization header middleware is wired, remove ?auth= query param
    apiFetch<MeResponse>(`/auth/me?auth=${encodeURIComponent(token)}`)
      .then(({ user, organization }) => {
        setUser(user);
        setOrganization(organization);
      })
      .catch(() => clearToken()) // token invalid / expired
      .finally(() => setIsLoading(false));
  }, []);

  const setSession = useCallback((token: string) => {
    setToken(token);
    apiFetch<MeResponse>(`/auth/me?auth=${encodeURIComponent(token)}`).then(
      ({ user, organization }) => {
        setUser(user);
        setOrganization(organization);
      },
    );
  }, []);

  const clearSession = useCallback(() => {
    clearToken();
    setUser(null);
    setOrganization(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        organization,
        isLoading,
        isAuthenticated: user !== null,
        setSession,
        clearSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
