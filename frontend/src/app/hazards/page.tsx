"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import api from "@/lib/api";
import type { Hazard, Paginated } from "@/lib/types";
import AuthGate from "@/components/AuthGate";
import Navbar from "@/components/Navbar";
import HazardBadge from "@/components/HazardBadge";

export default function HazardsPage() {
  return (
    <AuthGate>
      <Navbar />
      <Inner />
    </AuthGate>
  );
}

function Inner() {
  const [items, setItems] = useState<Hazard[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<Paginated<Hazard>>("/hazards/", { params: { page_size: 100 } })
      .then((r) => setItems(r.data.results))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="max-w-4xl mx-auto px-5 py-8">
      <div className="mb-6">
        <div className="meta-label mb-1">03 · Riscos</div>
        <h1 className="text-serif text-4xl text-biolab-700" style={{ letterSpacing: "-0.01em" }}>
          Categorias de risco · GHS
        </h1>
        <p className="text-sm text-biolab-900/65 mt-1">
          Riscos canônicos usados pelo motor de regras e atribuídos às substâncias.
        </p>
      </div>

      {loading ? (
        <div className="card p-12 text-center">
          <Loader2 className="h-6 w-6 animate-spin mx-auto text-biolab-500" />
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {items.map((h) => (
            <div key={h.id} className="card p-5">
              <div className="flex items-start justify-between mb-2 gap-3">
                <h3 className="font-display font-semibold text-biolab-900" style={{ letterSpacing: "-0.01em" }}>{h.name}</h3>
                <HazardBadge hazard={h} />
              </div>
              <p className="text-mono text-xs text-biolab-900/55 mb-2 tracking-wide uppercase">{h.code_display}</p>
              {h.description && (
                <p className="text-sm text-biolab-900/75 leading-relaxed">{h.description}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
