"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Loader2,
  Search,
  X,
  FlaskConical,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Plus,
} from "lucide-react";
import api from "@/lib/api";
import type {
  CompatibilityCheckResult,
  Paginated,
  RiskLevel,
  RiskStatus,
  SubstanceListItem,
} from "@/lib/types";
import AuthGate from "@/components/AuthGate";
import Navbar from "@/components/Navbar";
import StatusBadge from "@/components/StatusBadge";

const RULE_LABELS: Record<string, string> = {
  acid_plus_water: "Ácido + Água",
  acid_plus_base: "Ácido + Base",
  oxidizer_plus_flammable: "Oxidante + Inflamável",
  oxidizer_plus_organic: "Oxidante + Solvente orgânico",
  water_reactive_plus_water: "Reativo com água + Água",
  toxic_pair_advisory: "Par de substâncias tóxicas",
  corrosive_same_class: "Corrosivos da mesma classe",
  corrosive_plus_flammable: "Corrosivo + Inflamável",
  peroxide_former_advisory: "Formador de peróxidos",
  strong_acid_plus_cyanide: "Ácido forte + Cianeto",
  strong_acid_plus_sulfide: "Ácido forte + Sulfeto",
  bleach_plus_ammonia: "Hipoclorito + Amônia",
  bleach_plus_acid: "Hipoclorito + Ácido",
  nitric_acid_plus_organic: "Ácido nítrico + Orgânico",
};

function ruleLabel(ruleId: string): string {
  return RULE_LABELS[ruleId] ?? ruleId.replace(/_/g, " ");
}

export default function CheckPage() {
  return (
    <AuthGate>
      <Navbar />
      <CompatibilityChecker />
    </AuthGate>
  );
}

const RISK_LABEL: Record<RiskLevel, string> = {
  low: "Baixo",
  medium: "Médio",
  high: "Alto",
};

// Per-risk inline styles. Using CSS variables directly (instead of Tailwind
// arbitrary opacity classes) avoids JIT picking only some of the slash-opacity
// variants and dropping others — which left the banner background invisible.
const RISK_STYLE: Record<RiskLevel, React.CSSProperties> = {
  low:    { background: "color-mix(in srgb, var(--risk-low) 14%, white)",  color: "var(--risk-low)",  borderColor: "color-mix(in srgb, var(--risk-low) 35%, white)"  },
  medium: { background: "color-mix(in srgb, var(--risk-mid) 18%, white)",  color: "#8a6420",          borderColor: "color-mix(in srgb, var(--risk-mid) 45%, white)"  },
  high:   { background: "color-mix(in srgb, var(--risk-high) 14%, white)", color: "var(--risk-high)", borderColor: "color-mix(in srgb, var(--risk-high) 35%, white)" },
};

const STATUS_STYLE: Record<RiskStatus, { style: React.CSSProperties; icon: any; toneStyle: React.CSSProperties }> = {
  safe:    { icon: CheckCircle2,  style: { background: "color-mix(in srgb, var(--risk-low) 12%, white)",  borderColor: "color-mix(in srgb, var(--risk-low) 35%, white)"  }, toneStyle: { color: "var(--risk-low)" }  },
  unknown: { icon: AlertTriangle, style: { background: "color-mix(in srgb, var(--risk-mid) 16%, white)",  borderColor: "color-mix(in srgb, var(--risk-mid) 45%, white)"  }, toneStyle: { color: "#8a6420" }          },
  unsafe:  { icon: ShieldAlert,   style: { background: "color-mix(in srgb, var(--risk-high) 12%, white)", borderColor: "color-mix(in srgb, var(--risk-high) 35%, white)" }, toneStyle: { color: "var(--risk-high)" } },
};

function CompatibilityChecker() {
  const [results, setResults] = useState<SubstanceListItem[]>([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<SubstanceListItem[]>([]);
  const [result, setResult] = useState<CompatibilityCheckResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [searching, setSearching] = useState(false);

  // Server-side search: fetch matches as the user types (debounced).
  // Avoids the trap of pre-loading only the first N substances and missing
  // anything alphabetically below the cutoff.
  useEffect(() => {
    const q = search.trim();
    if (!q) {
      setResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setSearching(true);
      try {
        const { data } = await api.get<Paginated<SubstanceListItem>>(
          "/substances/",
          { params: { search: q, page_size: 12 } }
        );
        setResults(data.results);
      } finally {
        setSearching(false);
      }
    }, 200);
    return () => clearTimeout(timer);
  }, [search]);

  const filtered = useMemo(() => {
    const taken = new Set(selected.map((s) => s.id));
    return results.filter((s) => !taken.has(s.id)).slice(0, 8);
  }, [results, selected]);

  function add(s: SubstanceListItem) {
    if (selected.some((x) => x.id === s.id)) return;
    setSelected([...selected, s]);
    setSearch("");
    setResult(null);
  }
  function remove(id: number) {
    setSelected(selected.filter((s) => s.id !== id));
    setResult(null);
  }

  async function runCheck() {
    if (selected.length < 2) return;
    setError("");
    setSubmitting(true);
    setResult(null);
    try {
      const { data } = await api.post<CompatibilityCheckResult>(
        "/compatibility/check/",
        { substance_ids: selected.map((s) => s.id) },
      );
      setResult(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Falha ao executar a verificação.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="max-w-4xl mx-auto px-5 py-8">
      <div className="mb-6">
        <div className="meta-label mb-1">02 · Verificador</div>
        <h1 className="text-serif text-4xl text-biolab-700" style={{ letterSpacing: "-0.01em" }}>
          Verificar compatibilidade
        </h1>
        <p className="text-sm text-biolab-900/65 mt-1">
          Selecione 2 ou mais substâncias para analisar todas as combinações em pares.
        </p>
      </div>

      <div className="card p-5 mb-5">
        <div className="flex flex-wrap gap-2 mb-4 min-h-[40px]">
          {selected.length === 0 && (
            <span className="text-sm text-biolab-400 self-center">
              Nenhuma substância selecionada ainda.
            </span>
          )}
          {selected.map((s) => (
            <span
              key={s.id}
              className="inline-flex items-center gap-2 rounded-lg bg-biolab-50 border border-biolab-200 text-biolab-800 pl-3 pr-1 py-1 text-sm font-medium"
            >
              {s.name}
              <button
                onClick={() => remove(s.id)}
                className="rounded p-1 hover:bg-biolab-100 text-biolab-500"
                title="Remover"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </span>
          ))}
        </div>

        <div className="relative mb-3">
          <div className="flex items-stretch gap-3">
            <div className="grid place-items-center px-3 border border-biolab-200 rounded-sm bg-biolab-50 text-biolab-500">
              <Search className="h-4 w-4" />
            </div>
            <div className="relative flex-1">
              <input
                className="input"
                placeholder="Buscar e adicionar substância..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              {searching && (
                <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-biolab-400" />
              )}
            </div>
          </div>
          {search && !searching && filtered.length === 0 && (
            <div className="absolute z-10 left-0 right-0 top-full mt-1 bg-white border border-biolab-200 rounded-sm shadow-card px-3.5 py-3 text-sm text-biolab-500">
              Nenhuma substância encontrada para "{search}".
            </div>
          )}
          {search && filtered.length > 0 && (
            <div className="absolute z-10 left-0 right-0 top-full mt-1 bg-white border border-biolab-200 rounded-sm shadow-card overflow-hidden">
              {filtered.map((s) => (
                <button
                  key={s.id}
                  onClick={() => add(s)}
                  className="flex items-center gap-3 w-full px-3.5 py-2.5 text-left hover:bg-biolab-50 transition border-b border-biolab-100 last:border-b-0"
                >
                  <Plus className="h-4 w-4 text-biolab-400" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-biolab-900 truncate">{s.name}</div>
                    {s.formula && (
                      <div className="text-xs text-biolab-500 font-mono">{s.formula}</div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <button
          onClick={runCheck}
          disabled={selected.length < 2 || submitting}
          className="btn-primary w-full"
        >
          {submitting ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <FlaskConical className="h-4 w-4" />
          )}
          Verificar
        </button>

        {error && (
          <div className="mt-3 text-sm bg-[color:var(--risk-high)]/10 border border-[color:var(--risk-high)]/30 text-[color:var(--risk-high)] rounded-sm px-3 py-2">
            {error}
          </div>
        )}
      </div>

      {result && <ResultPanel result={result} />}
    </main>
  );
}

function ResultPanel({ result }: { result: CompatibilityCheckResult }) {
  const banner = STATUS_STYLE[result.overall_status];
  const Icon = banner.icon;
  return (
    <div className="space-y-5">
      <div className="rounded-sm border-2 p-5" style={banner.style}>
        <div className="flex items-start gap-3">
          <Icon className="h-6 w-6 mt-0.5 shrink-0" style={banner.toneStyle} />
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <StatusBadge status={result.overall_status} />
              <span
                className="text-mono text-[11px] px-2 py-0.5 rounded-sm font-medium border tracking-wide uppercase"
                style={RISK_STYLE[result.overall_risk]}
              >
                Risco {RISK_LABEL[result.overall_risk]}
              </span>
            </div>
            <p className="font-medium leading-snug" style={banner.toneStyle}>
              {result.overall_message}
            </p>
          </div>
        </div>
      </div>

      {result.required_ppe.length > 0 && (
        <div className="card p-5">
          <h2 className="font-display font-bold text-biolab-900 mb-2">EPIs combinados</h2>
          <div className="flex flex-wrap gap-2">
            {result.required_ppe.map((p) => (
              <span key={p} className="badge bg-biolab-50 text-biolab-700 border border-biolab-200">
                {p}
              </span>
            ))}
          </div>
        </div>
      )}

      {result.critical_alerts.length > 0 && (
        <div className="card p-5 border-l-4 border-[color:var(--risk-high)]/60 bg-[color:var(--risk-high)]/5">
          <div className="meta-label mb-1" style={{ color: "var(--risk-high)" }}>Alerta · LVL 03</div>
          <h2 className="font-display font-semibold text-[color:var(--risk-high)] mb-2" style={{ letterSpacing: "-0.01em" }}>Alertas críticos</h2>
          <ul className="space-y-1.5 text-sm text-[color:var(--risk-high)]/90">
            {result.critical_alerts.map((a, i) => (
              <li key={i} className="leading-relaxed">• {a}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="card p-5">
        <h2 className="font-display font-bold text-biolab-900 mb-4">
          Detalhes por par ({result.pairs.length})
        </h2>
        <div className="space-y-3">
          {result.pairs.map((p, i) => (
            <div key={i} className="border border-biolab-100 rounded-xl p-4">
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="font-medium text-biolab-900">
                  {p.substance_a_name} <span className="text-biolab-400">+</span> {p.substance_b_name}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <StatusBadge status={p.status} />
                  <span
                    className="text-mono text-[11px] px-2 py-0.5 rounded-sm font-medium border tracking-wide uppercase"
                    style={RISK_STYLE[p.risk_level]}
                  >
                    {RISK_LABEL[p.risk_level]}
                  </span>
                </div>
              </div>
              {p.reaction_type && (
                <p className="text-xs uppercase tracking-wide text-biolab-500 mb-1">
                  Tipo de reação
                </p>
              )}
              {p.reaction_type && (
                <p className="text-sm text-biolab-800 mb-2">{p.reaction_type}</p>
              )}
              {p.message && (
                <p className="text-sm text-biolab-700 leading-relaxed">{p.message}</p>
              )}
              {p.findings.length > 0 && (
                <details className="mt-3">
                  <summary className="cursor-pointer text-xs text-biolab-500 hover:text-biolab-700">
                    Ver regras aplicadas ({p.findings.length})
                  </summary>
                  <ul className="mt-2 space-y-1.5 pl-3 border-l-2 border-biolab-100">
                    {p.findings.map((f, fi) => (
                      <li key={fi} className="text-xs text-biolab-700">
                        <span className="font-medium text-biolab-600">{ruleLabel(f.rule_id)}</span> — {f.message}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
              <p className="text-xs text-biolab-400 mt-3">
                Fontes: {p.sources.map(s => ({ rules: "Regras do sistema", record: "Registro curado", fallback_unknown: "Sem dados (segurança)" }[s] ?? s)).join(", ")}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
