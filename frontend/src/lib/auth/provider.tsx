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

interface CachedAuthData {
  user: AuthUser;
  organization: AuthOrganization;
  tokenHash: string;
}

// Mock user for development/testing
const MOCK_DEV_USER: AuthUser = {
  id: "dev-user-123",
  email: "dev@localhost.local",
  full_name: "Dev User",
};

const MOCK_DEV_ORG: AuthOrganization = {
  id: "dev-org-123",
  name: "Dev Organization",
  slug: "dev-org",
};

// Cache helper functions (only run in browser)
function getCachedAuthData(): CachedAuthData | null {
  if (typeof window === "undefined") return null;
  try {
    const cached = localStorage.getItem("auth_cache");
    return cached ? JSON.parse(cached) : null;
  } catch {
    return null;
  }
}

function setCachedAuthData(
  user: AuthUser,
  organization: AuthOrganization,
  token: string,
): void {
  if (typeof window === "undefined") return;
  try {
    const tokenHash = token.substring(0, 20); // First 20 chars as hash
    localStorage.setItem(
      "auth_cache",
      JSON.stringify({ user, organization, tokenHash }),
    );
  } catch {
    // Ignore localStorage errors
  }
}

function clearCachedAuthData(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem("auth_cache");
  } catch {
    // Ignore localStorage errors
  }
}

function isTokenHashMatch(
  cachedTokenHash: string,
  currentToken: string,
): boolean {
  return cachedTokenHash === currentToken.substring(0, 20);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [organization, setOrganization] = useState<AuthOrganization | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);

  // Hydrate session from cookie on mount
  useEffect(() => {
    // Dev mode: bypass auth if ?devmode=1 in URL
    const isDev =
      typeof window !== "undefined" &&
      new URLSearchParams(window.location.search).has("devmode");

    if (isDev) {
      setUser(MOCK_DEV_USER);
      setOrganization(MOCK_DEV_ORG);
      setIsLoading(false);
      return;
    }

    const token = getToken();
    const devmode =
      new URLSearchParams(window.location.search).get("devmode") === "true";

    if (!token) {
      if (devmode) {
        // Dev mode: create mock session
        setUser({
          id: "dev-user",
          email: "dev@alphacon.ai",
          full_name: "Dev User",
        });
        setOrganization({
          id: "dev-org",
          name: "Dev Organization",
          slug: "dev-org",
        });
      }
      clearCachedAuthData();
      setIsLoading(false);
      return;
    }

    // Try to restore from cache first (faster UX on refresh)
    const cached = getCachedAuthData();
    if (cached && isTokenHashMatch(cached.tokenHash, token)) {
      setUser(cached.user);
      setOrganization(cached.organization);
    }

    // TODO: Once Authorization header middleware is wired, remove ?auth= query param
    apiFetch<MeResponse>(`/auth/me?auth=${encodeURIComponent(token)}`)
      .then(({ user, organization }) => {
        setUser(user);
        setOrganization(organization);
        setCachedAuthData(user, organization, token);
      })
      .catch(() => {
        clearCachedAuthData();
        clearToken();
      })
      .finally(() => setIsLoading(false));
  }, []);

  const setSession = useCallback((token: string) => {
    setToken(token);
    apiFetch<MeResponse>(`/auth/me?auth=${encodeURIComponent(token)}`)
      .then(({ user, organization }) => {
        setUser(user);
        setOrganization(organization);
        setCachedAuthData(user, organization, token);
      })
      .catch((error) => {
        console.error("Failed to fetch user session:", error);
        clearCachedAuthData();
        clearToken();
      });
  }, []);

  const clearSession = useCallback(() => {
    clearToken();
    clearCachedAuthData();
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
