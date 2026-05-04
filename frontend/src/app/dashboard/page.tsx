"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Search,
  Loader2,
  FlaskRound,
  ArrowRight,
  Plus,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import api from "@/lib/api";
import type { Paginated, SubstanceListItem } from "@/lib/types";
import AuthGate from "@/components/AuthGate";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/lib/auth";

const PAGE_SIZE = 24;

export default function DashboardPage() {
  return (
    <AuthGate>
      <Navbar />
      <SubstanceList />
    </AuthGate>
  );
}

function SubstanceList() {
  const { user } = useAuth();
  const [items, setItems] = useState<SubstanceListItem[]>([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const totalPages = Math.max(1, Math.ceil(count / PAGE_SIZE));

  useEffect(() => {
    setPage(1);
  }, [search]);

  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, page]);

  async function load() {
    setLoading(true);
    try {
      const { data } = await api.get<Paginated<SubstanceListItem>>(
        "/substances/",
        { params: { search, page, page_size: PAGE_SIZE } }
      );
      setItems(data.results);
      setCount(data.count);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-6xl mx-auto px-5 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="meta-label mb-1">01 · Catálogo</div>
          <h1 className="text-serif text-4xl text-biolab-700" style={{ letterSpacing: "-0.01em" }}>
            Substâncias
          </h1>
          <p className="text-sm text-biolab-900/65 mt-1">Catálogo de reagentes e propriedades</p>
        </div>
        <div className="flex items-center gap-2">
          {user?.is_supervisor && (
            <Link href="/substances/new" className="btn-ghost text-sm">
              <Plus className="h-4 w-4" />
              Nova substância
            </Link>
          )}
          <Link href="/check" className="btn-primary text-sm">
            <FlaskRound className="h-4 w-4" />
            Verificar compatibilidade
          </Link>
        </div>
      </div>

      <div className="card p-4 mb-5">
        <div className="flex items-stretch gap-3">
          <div className="grid place-items-center px-3 border border-biolab-200 rounded-sm bg-biolab-50 text-biolab-500">
            <Search className="h-4 w-4" />
          </div>
          <input
            type="text"
            placeholder="Buscar por nome, fórmula ou CAS..."
            className="input flex-1"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div className="card p-12 text-center text-biolab-500">
          <Loader2 className="h-6 w-6 animate-spin mx-auto" />
        </div>
      ) : items.length === 0 ? (
        <div className="card p-12 text-center text-biolab-600">
          Nenhuma substância encontrada.
        </div>
      ) : (
        <>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {items.map((s) => (
              <Link
                key={s.id}
                href={`/substances/${s.id}`}
                className="card p-5 hover:border-biolab-300 hover:shadow-md transition group"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="min-w-0">
                    <h3 className="font-display font-semibold text-biolab-900 truncate" style={{ letterSpacing: "-0.01em" }}>
                      {s.name}
                    </h3>
                    {s.formula && (
                      <p className="text-mono text-sm text-biolab-500 mt-0.5">{s.formula}</p>
                    )}
                  </div>
                  <ArrowRight className="h-4 w-4 text-biolab-400 group-hover:text-biolab-600 transition shrink-0" />
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-mono text-biolab-900/55 tracking-wide">
                    {s.physical_state_display.toUpperCase()}
                    {s.cas_number && ` · ${s.cas_number}`}
                  </span>
                  {s.hazard_codes.length > 0 && (
                    <span className="badge badge-unknown">
                      {s.hazard_codes.length} risco{s.hazard_codes.length > 1 ? "s" : ""}
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>

          <Pagination
            page={page}
            totalPages={totalPages}
            count={count}
            pageSize={PAGE_SIZE}
            shown={items.length}
            onChange={setPage}
          />
        </>
      )}
    </main>
  );
}

function Pagination({
  page,
  totalPages,
  count,
  pageSize,
  shown,
  onChange,
}: {
  page: number;
  totalPages: number;
  count: number;
  pageSize: number;
  shown: number;
  onChange: (p: number) => void;
}) {
  if (totalPages <= 1) return null;

  const start = (page - 1) * pageSize + 1;
  const end = start + shown - 1;

  return (
    <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
      <p className="text-xs text-biolab-500">
        Mostrando <span className="font-medium text-biolab-700">{start}–{end}</span>{" "}
        de <span className="font-medium text-biolab-700">{count}</span>
      </p>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onChange(page - 1)}
          disabled={page <= 1}
          className="btn-ghost text-sm disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="h-4 w-4" />
          Anterior
        </button>
        {pageRange(page, totalPages).map((p, i) =>
          p === "…" ? (
            <span key={`gap-${i}`} className="px-2 text-biolab-400 text-sm">
              …
            </span>
          ) : (
            <button
              key={p}
              onClick={() => onChange(p as number)}
              className={`min-w-[36px] h-9 px-2 rounded-lg text-sm font-medium transition ${
                p === page
                  ? "bg-biolab-600 text-white"
                  : "text-biolab-700 hover:bg-biolab-50"
              }`}
            >
              {p}
            </button>
          )
        )}
        <button
          onClick={() => onChange(page + 1)}
          disabled={page >= totalPages}
          className="btn-ghost text-sm disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Próxima
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

/**
 * Build a compact page-number list with ellipses, e.g.:
 *   1, 2, 3, 4, 5 (when totalPages <= 7)
 *   1, …, 4, 5, 6, …, 12
 */
function pageRange(current: number, total: number): (number | "…")[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  const pages: (number | "…")[] = [1];
  const left = Math.max(2, current - 1);
  const right = Math.min(total - 1, current + 1);
  if (left > 2) pages.push("…");
  for (let i = left; i <= right; i++) pages.push(i);
  if (right < total - 1) pages.push("…");
  pages.push(total);
  return pages;
}
