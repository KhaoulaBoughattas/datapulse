"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { api, getToken, clearToken } from "./api-client";
import type { CurrentUser, Role } from "./types";

interface AuthContextValue {
  user: CurrentUser | null;
  loading: boolean;
  logout: () => void;
  can: (permission: string) => boolean;
}

const ROLE_PERMISSIONS: Record<Role, Set<string>> = {
  OWNER: new Set(["*"]),
  ADMIN: new Set(["user:read", "user:write", "pipeline:read", "pipeline:write", "data_source:read", "data_source:write", "dataset:read", "quality:read", "quality:write"]),
  DATA_ENGINEER: new Set(["pipeline:read", "pipeline:write", "data_source:read", "data_source:write", "dataset:read", "quality:read", "quality:write"]),
  ANALYST: new Set(["pipeline:read", "data_source:read", "dataset:read", "quality:read"]),
  VIEWER: new Set(["pipeline:read", "dataset:read", "quality:read"]),
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      router.replace("/login");
      return;
    }
    api
      .get<CurrentUser>("/auth/me")
      .then(setUser)
      .catch(() => router.replace("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  const logout = () => {
    clearToken();
    setUser(null);
    router.replace("/login");
  };

  const can = (permission: string): boolean => {
    if (!user) return false;
    const allowed = ROLE_PERMISSIONS[user.role];
    return allowed.has("*") || allowed.has(permission);
  };

  return <AuthContext.Provider value={{ user, loading, logout, can }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
