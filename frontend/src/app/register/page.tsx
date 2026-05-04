"use client";

import { useState } from "react";
import Link from "next/link";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/lib/auth";
import Logo from "@/components/Logo";

export default function RegisterPage() {
  const { register } = useAuth();
  const [form, setForm] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    institution: "",
    registration_number: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field: keyof typeof form, value: string) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register(form);
    } catch (err: any) {
      const data = err?.response?.data;
      const msg =
        (data && typeof data === "object" && Object.values(data)?.[0]) ||
        "Falha ao criar conta.";
      setError(Array.isArray(msg) ? msg[0] : String(msg));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen grid place-items-center px-5 py-10">
      <div className="w-full max-w-md">
        <div className="flex justify-center mb-8">
          <Logo size="lg" />
        </div>
        <div className="card p-7">
          <div className="meta-label mb-2">Sign up</div>
          <h1 className="text-serif text-3xl text-biolab-700 mb-1" style={{ letterSpacing: "-0.01em" }}>
            Criar conta
          </h1>
          <p className="text-sm text-biolab-900/65 mb-6">
            Cadastre-se para acessar o sistema.
          </p>

          <form onSubmit={onSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-biolab-700 mb-1.5">Nome</label>
                <input
                  type="text"
                  className="input"
                  value={form.first_name}
                  onChange={(e) => update("first_name", e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-biolab-700 mb-1.5">Sobrenome</label>
                <input
                  type="text"
                  className="input"
                  value={form.last_name}
                  onChange={(e) => update("last_name", e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-biolab-700 mb-1.5">Email</label>
              <input
                type="email"
                className="input"
                value={form.email}
                onChange={(e) => update("email", e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-biolab-700 mb-1.5">Senha</label>
              <input
                type="password"
                className="input"
                value={form.password}
                onChange={(e) => update("password", e.target.value)}
                placeholder="Mínimo 8 caracteres"
                required
                minLength={8}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-biolab-700 mb-1.5">
                Instituição (opcional)
              </label>
              <input
                type="text"
                className="input"
                value={form.institution}
                onChange={(e) => update("institution", e.target.value)}
                placeholder="Ex: UFRJ, Hospital São Lucas..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-biolab-700 mb-1.5">
                Registro profissional (opcional)
              </label>
              <input
                type="text"
                className="input"
                value={form.registration_number}
                onChange={(e) => update("registration_number", e.target.value)}
                placeholder="Ex: CRBM 12345"
              />
            </div>

            {error && (
              <div className="text-sm bg-[color:var(--risk-high)]/10 border border-[color:var(--risk-high)]/30 text-[color:var(--risk-high)] rounded-sm px-3 py-2">
                {error}
              </div>
            )}

            <button type="submit" className="btn-primary w-full" disabled={submitting}>
              {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Criar conta
            </button>
          </form>

          <p className="text-sm text-biolab-900/65 text-center mt-6">
            Já tem conta?{" "}
            <Link href="/login" className="text-biolab-500 font-semibold hover:underline">
              Entrar
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
