"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save, Loader2 } from "lucide-react";
import api from "@/lib/api";
import type { Hazard } from "@/lib/types";
import AuthGate from "@/components/AuthGate";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/lib/auth";

export default function NewSubstancePage() {
  return (
    <AuthGate>
      <Navbar />
      <Inner />
    </AuthGate>
  );
}

interface FormState {
  name: string;
  formula: string;
  cas_number: string;
  description: string;
  physical_state: string;
  molar_mass: string;
  ph_value: string;
  is_acid: boolean;
  is_base: boolean;
  is_water: boolean;
  is_organic_solvent: boolean;
  required_ppe: string;
  handling_notes: string;
  critical_alerts: string;
  storage_instructions: string;
  storage_incompatibilities: string;
  hazard_ids: number[];
}

const INITIAL: FormState = {
  name: "",
  formula: "",
  cas_number: "",
  description: "",
  physical_state: "liquid",
  molar_mass: "",
  ph_value: "",
  is_acid: false,
  is_base: false,
  is_water: false,
  is_organic_solvent: false,
  required_ppe: "",
  handling_notes: "",
  critical_alerts: "",
  storage_instructions: "",
  storage_incompatibilities: "",
  hazard_ids: [],
};

function Inner() {
  const router = useRouter();
  const { user } = useAuth();
  const [form, setForm] = useState<FormState>(INITIAL);
  const [hazards, setHazards] = useState<Hazard[]>([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    api.get<{ results?: Hazard[] } | Hazard[]>("/hazards/").then((r) => {
      const data = r.data as any;
      setHazards(Array.isArray(data) ? data : data.results || []);
    });
  }, []);

  if (user && !user.is_supervisor) {
    return (
      <main className="max-w-3xl mx-auto px-5 py-10">
        <div className="card p-6 text-center text-biolab-700">
          Apenas supervisores podem cadastrar substâncias.
        </div>
      </main>
    );
  }

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function toggleHazard(id: number) {
    setForm((f) => ({
      ...f,
      hazard_ids: f.hazard_ids.includes(id)
        ? f.hazard_ids.filter((x) => x !== id)
        : [...f.hazard_ids, id],
    }));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const payload: any = {
        ...form,
        molar_mass: form.molar_mass || null,
        ph_value: form.ph_value || null,
        required_ppe: form.required_ppe
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
      };
      const { data } = await api.post<{ id: number }>("/substances/", payload);
      router.push(`/substances/${data.id}`);
    } catch (err: any) {
      const detail = err?.response?.data;
      setError(
        typeof detail === "string"
          ? detail
          : JSON.stringify(detail || err?.message || "Erro ao salvar")
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="max-w-3xl mx-auto px-5 py-8">
      <button onClick={() => router.back()} className="btn-ghost mb-4 -ml-3">
        <ArrowLeft className="h-4 w-4" /> Voltar
      </button>

      <div className="mb-5">
        <h1 className="font-display text-2xl font-bold text-biolab-900">
          Nova substância
        </h1>
        <p className="text-sm text-biolab-600">
          Cadastro manual no catálogo de reagentes.
        </p>
      </div>

      <form onSubmit={submit} className="card p-6 space-y-5">
        <Section title="Identificação">
          <Field label="Nome *">
            <input
              required
              className="input"
              value={form.name}
              onChange={(e) => update("name", e.target.value)}
            />
          </Field>
          <div className="grid sm:grid-cols-2 gap-3">
            <Field label="Fórmula">
              <input
                className="input"
                value={form.formula}
                onChange={(e) => update("formula", e.target.value)}
              />
            </Field>
            <Field label="CAS">
              <input
                className="input"
                value={form.cas_number}
                onChange={(e) => update("cas_number", e.target.value)}
              />
            </Field>
          </div>
          <Field label="Descrição">
            <textarea
              className="input min-h-[60px]"
              value={form.description}
              onChange={(e) => update("description", e.target.value)}
            />
          </Field>
        </Section>

        <Section title="Propriedades físicas">
          <div className="grid sm:grid-cols-3 gap-3">
            <Field label="Estado físico">
              <select
                className="input"
                value={form.physical_state}
                onChange={(e) => update("physical_state", e.target.value)}
              >
                <option value="solid">Sólido</option>
                <option value="liquid">Líquido</option>
                <option value="gas">Gás</option>
                <option value="aqueous">Solução aquosa</option>
              </select>
            </Field>
            <Field label="Massa molar (g/mol)">
              <input
                type="number"
                step="0.001"
                className="input"
                value={form.molar_mass}
                onChange={(e) => update("molar_mass", e.target.value)}
              />
            </Field>
            <Field label="pH">
              <input
                type="number"
                step="0.01"
                className="input"
                value={form.ph_value}
                onChange={(e) => update("ph_value", e.target.value)}
              />
            </Field>
          </div>
        </Section>

        <Section title="Reatividade (motor de regras)">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {[
              ["is_acid", "É ácido"],
              ["is_base", "É base"],
              ["is_water", "É água"],
              ["is_organic_solvent", "Solvente orgânico"],
            ].map(([key, label]) => (
              <label
                key={key}
                className="flex items-center gap-2 text-sm text-biolab-800"
              >
                <input
                  type="checkbox"
                  checked={(form as any)[key]}
                  onChange={(e) => update(key as any, e.target.checked as any)}
                />
                {label}
              </label>
            ))}
          </div>
        </Section>

        <Section title="Riscos">
          <div className="flex flex-wrap gap-2">
            {hazards.map((h) => {
              const active = form.hazard_ids.includes(h.id);
              return (
                <button
                  key={h.id}
                  type="button"
                  onClick={() => toggleHazard(h.id)}
                  className={`badge border ${
                    active
                      ? "bg-biolab-600 text-white border-biolab-600"
                      : "bg-white text-biolab-700 border-biolab-200"
                  }`}
                >
                  {h.name}
                </button>
              );
            })}
          </div>
        </Section>

        <Section title="Manuseio & EPIs">
          <Field label="EPIs (separados por vírgula)">
            <input
              className="input"
              placeholder="luvas nitrílicas, óculos de proteção, jaleco"
              value={form.required_ppe}
              onChange={(e) => update("required_ppe", e.target.value)}
            />
          </Field>
          <Field label="Cuidados ao manipular">
            <textarea
              className="input min-h-[60px]"
              value={form.handling_notes}
              onChange={(e) => update("handling_notes", e.target.value)}
            />
          </Field>
          <Field label="Alertas críticos">
            <textarea
              className="input min-h-[60px]"
              value={form.critical_alerts}
              onChange={(e) => update("critical_alerts", e.target.value)}
            />
          </Field>
        </Section>

        <Section title="Armazenamento">
          <Field label="Instruções">
            <textarea
              className="input min-h-[60px]"
              value={form.storage_instructions}
              onChange={(e) => update("storage_instructions", e.target.value)}
            />
          </Field>
          <Field label="Incompatibilidades">
            <textarea
              className="input min-h-[60px]"
              value={form.storage_incompatibilities}
              onChange={(e) =>
                update("storage_incompatibilities", e.target.value)
              }
            />
          </Field>
        </Section>

        {error && (
          <div className="rounded-sm bg-[color:var(--risk-high)]/10 border border-[color:var(--risk-high)]/30 px-3 py-2 text-sm text-[color:var(--risk-high)]">
            {error}
          </div>
        )}

        <div className="flex items-center justify-end gap-2 pt-2 border-t border-biolab-100">
          <button
            type="button"
            className="btn-ghost"
            onClick={() => router.back()}
            disabled={saving}
          >
            Cancelar
          </button>
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            Salvar
          </button>
        </div>
      </form>
    </main>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h2 className="font-display font-bold text-biolab-900 mb-3">{title}</h2>
      <div className="space-y-3">{children}</div>
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="text-xs uppercase tracking-wide text-biolab-500 mb-1 block">
        {label}
      </span>
      {children}
    </label>
  );
}
