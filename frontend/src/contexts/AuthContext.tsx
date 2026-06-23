"use client";

// Client: holds auth state and the bearer token (browser-only storage).

import { createContext, useContext, useEffect, useState } from "react";

import { authApi, type CurrentUser, TOKEN_STORAGE_KEY } from "@/lib/api";

interface AuthContextValue {
  user: CurrentUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: {
    email: string;
    password: string;
    full_name: string;
    organization_name?: string;
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function storeToken(token: string): void {
  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!window.localStorage.getItem(TOKEN_STORAGE_KEY)) {
      setLoading(false);
      return;
    }
    authApi
      .me()
      .then(setUser)
      .catch(() => window.localStorage.removeItem(TOKEN_STORAGE_KEY))
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string): Promise<void> {
    const { access_token } = await authApi.login({ email, password });
    storeToken(access_token);
    setUser(await authApi.me());
  }

  async function signup(data: {
    email: string;
    password: string;
    full_name: string;
    organization_name?: string;
  }): Promise<void> {
    const { access_token } = await authApi.signup(data);
    storeToken(access_token);
    setUser(await authApi.me());
  }

  function logout(): void {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (value === null) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return value;
}
