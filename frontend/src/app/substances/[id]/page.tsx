"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Loader2,
  ArrowLeft,
  Beaker,
  Shield,
  Archive,
  AlertTriangle,
  Trash2,
} from "lucide-react";
import api from "@/lib/api";
import type { Substance } from "@/lib/types";
import AuthGate from "@/components/AuthGate";
import Navbar from "@/components/Navbar";
import HazardBadge from "@/components/HazardBadge";
import { useAuth } from "@/lib/auth";

export default function SubstanceDetailPage() {
  return (
    <AuthGate>
      <Navbar />
      <Inner />
    </AuthGate>
  );
}

function Inner() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const [substance, setSubstance] = useState<Substance | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    api
      .get<Substance>(`/substances/${params.id}/`)
      .then((r) => setSubstance(r.data))
      .finally(() => setLoading(false));
  }, [params.id]);

  async function handleDelete() {
    if (!substance) return;
    if (!confirm(`Remover "${substance.name}" do catálogo? Esta ação não pode ser desfeita.`)) return;
    setDeleting(true);
    try {
      await api.delete(`/substances/${substance.id}/`);
      router.push("/dashboard");
    } catch (err: any) {
      alert(err?.response?.data?.detail || "Erro ao remover substância.");
      setDeleting(false);
    }
  }

  if (loading) {
    return (
      <div className="grid place-items-center py-20 text-biolab-500">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }
  if (!substance) {
    return <div className="max-w-3xl mx-auto p-10 text-center">Substância não encontrada.</div>;
  }

  return (
    <main className="max-w-4xl mx-auto px-5 py-8">
      <div className="flex items-center justify-between mb-4">
        <button onClick={() => router.back()} className="btn-ghost -ml-3">
          <ArrowLeft className="h-4 w-4" /> Voltar
        </button>
        {user?.is_supervisor && (
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="btn-ghost text-[color:var(--risk-high)] hover:bg-[color:var(--risk-high)]/10"
            title="Remover substância"
          >
            {deleting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
            Remover
          </button>
        )}
      </div>

      <div className="card p-7 mb-5">
        <div className="flex items-start gap-4 mb-3">
          <div className="h-14 w-14 rounded-xl bg-biolab-50 grid place-items-center text-biolab-600">
            <Beaker className="h-6 w-6" />
          </div>
          <div className="min-w-0 flex-1">
            <h1 className="font-display text-3xl font-extrabold text-biolab-900 leading-tight">
              {substance.name}
            </h1>
            {substance.formula && (
              <p className="text-biolab-500 font-mono mt-1">{substance.formula}</p>
            )}
          </div>
        </div>

        {substance.description && (
          <p className="text-biolab-700 leading-relaxed mb-4">{substance.description}</p>
        )}

        <dl className="grid sm:grid-cols-3 gap-3 text-sm">
          <Field label="Estado físico" value={substance.physical_state_display} />
          {substance.cas_number && <Field label="CAS" value={substance.cas_number} />}
          {substance.molar_mass && <Field label="Massa molar" value={`${substance.molar_mass} g/mol`} />}
          {substance.ph_value && <Field label="pH" value={substance.ph_value} />}
        </dl>
      </div>

      {substance.hazards.length > 0 && (
        <Section icon={Shield} title="Riscos">
          <div className="flex flex-wrap gap-2">
            {substance.hazards.map((h) => (
              <HazardBadge key={h.id} hazard={h} />
            ))}
          </div>
        </Section>
      )}

      {substance.critical_alerts && (
        <div className="card p-5 mb-5 border-l-4 border-[color:var(--risk-high)]/60 bg-[color:var(--risk-high)]/5">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-[color:var(--risk-high)] mt-0.5 shrink-0" />
            <div>
              <div className="meta-label mb-1" style={{ color: "var(--risk-high)" }}>Alerta · LVL 03</div>
              <p className="font-display font-semibold text-[color:var(--risk-high)] mb-1" style={{ letterSpacing: "-0.01em" }}>Alertas críticos</p>
              <p className="text-sm text-[color:var(--risk-high)]/90 leading-relaxed">{substance.critical_alerts}</p>
            </div>
          </div>
        </div>
      )}

      {(substance.required_ppe.length > 0 || substance.handling_notes) && (
        <Section icon={Shield} title="Manuseio & EPIs">
          {substance.required_ppe.length > 0 && (
            <div className="mb-3">
              <p className="text-xs uppercase tracking-wide text-biolab-500 mb-2">EPIs recomendados</p>
              <div className="flex flex-wrap gap-2">
                {substance.required_ppe.map((p) => (
                  <span key={p} className="badge bg-biolab-50 text-biolab-700 border border-biolab-200">
                    {p}
                  </span>
                ))}
              </div>
            </div>
          )}
          {substance.handling_notes && (
            <p className="text-sm text-biolab-700 leading-relaxed">{substance.handling_notes}</p>
          )}
        </Section>
      )}

      {(substance.storage_instructions || substance.storage_incompatibilities) && (
        <Section icon={Archive} title="Armazenamento">
          {substance.storage_instructions && (
            <p className="text-sm text-biolab-700 leading-relaxed mb-3">
              {substance.storage_instructions}
            </p>
          )}
          {substance.storage_incompatibilities && (
            <div>
              <p className="text-xs uppercase tracking-wide text-biolab-500 mb-1">Incompatibilidades</p>
              <p className="text-sm text-biolab-800">{substance.storage_incompatibilities}</p>
            </div>
          )}
        </Section>
      )}
    </main>
  );
}

function Section({
  icon: Icon,
  title,
  children,
}: {
  icon: any;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="card p-5 mb-5">
      <div className="flex items-center gap-2 mb-3">
        <Icon className="h-4 w-4 text-biolab-500" />
        <h2 className="font-display font-bold text-biolab-900">{title}</h2>
      </div>
      {children}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-biolab-50/40 rounded-lg px-3 py-2">
      <dt className="text-xs uppercase tracking-wide text-biolab-500">{label}</dt>
      <dd className="text-biolab-900 font-medium">{value}</dd>
    </div>
  );
}
