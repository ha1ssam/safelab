"use client";

import { useState } from "react";
import Link from "next/link";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/lib/auth";
import Logo from "@/components/Logo";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(
        err?.response?.data?.non_field_errors?.[0] ||
        err?.response?.data?.detail ||
        "Falha no login. Verifique suas credenciais."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen grid place-items-center px-5">
      <div className="w-full max-w-md">
        <div className="flex justify-center mb-8">
          <Logo size="lg" />
        </div>
        <div className="card p-7">
          <div className="meta-label mb-2">Sign in</div>
          <h1 className="text-serif text-3xl text-biolab-700 mb-1" style={{ letterSpacing: "-0.01em" }}>
            Entrar
          </h1>
          <p className="text-sm text-biolab-900/65 mb-6">
            Acesse sua conta para consultar substâncias e compatibilidades.
          </p>

          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-biolab-700 mb-1.5">Email</label>
              <input
                type="email"
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="voce@laboratorio.com"
                required
                autoFocus
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-biolab-700 mb-1.5">Senha</label>
              <input
                type="password"
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            {error && (
              <div className="text-sm bg-[color:var(--risk-high)]/10 border border-[color:var(--risk-high)]/30 text-[color:var(--risk-high)] rounded-sm px-3 py-2">
                {error}
              </div>
            )}

            <button type="submit" className="btn-primary w-full" disabled={submitting}>
              {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Entrar
            </button>
          </form>

          <p className="text-sm text-biolab-900/65 text-center mt-6">
            Não tem conta?{" "}
            <Link href="/register" className="text-biolab-500 font-semibold hover:underline">
              Criar conta
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
