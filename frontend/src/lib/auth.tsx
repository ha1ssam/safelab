/**
 * Authentication context — wraps the app with the current user state.
 * Auth state is hydrated from /api/auth/me/ on mount; the JWT lives in
 * an HttpOnly cookie set by the backend.
 */

"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import type { User } from "@/lib/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name?: string;
  institution?: string;
  registration_number?: string;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  async function refresh() {
    try {
      const { data } = await api.get<User>("/auth/me/");
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function login(email: string, password: string) {
    const { data } = await api.post<{ user: User }>("/auth/login/", {
      email,
      password,
    });
    setUser(data.user);
    router.push("/dashboard");
  }

  async function register(payload: RegisterPayload) {
    const { data } = await api.post<{ user: User }>("/auth/register/", payload);
    setUser(data.user);
    router.push("/dashboard");
  }

  async function logout() {
    try {
      await api.post("/auth/logout/");
    } catch {
      // Ignore — we're clearing local state regardless
    }
    setUser(null);
    router.push("/login");
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth deve ser usado dentro de <AuthProvider>");
  return ctx;
}
