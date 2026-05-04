"use client";

import Link from "next/link";
import { ArrowRight, ShieldCheck, FlaskConical, Beaker, Database } from "lucide-react";
import Logo, { MarkA } from "@/components/Logo";

export default function Home() {
  return (
    <div className="min-h-screen relative">
      {/* Mono meta strip — top of page, like a brand canvas */}
      <div className="hidden sm:flex justify-between text-mono text-[10px] tracking-[0.18em] uppercase text-biolab-900/45 px-6 pt-3">
        <span>SafeLab · Brand System</span>
        <span>v0.1 · 2026</span>
      </div>

      <header className="max-w-6xl mx-auto px-5 py-5 flex items-center justify-between">
        <Logo size="md" />
        <div className="flex items-center gap-3">
          <Link href="/login" className="btn-ghost text-sm">Entrar</Link>
          <Link href="/register" className="btn-primary text-sm">
            Criar conta <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-5 pt-10 pb-24">
        <section className="text-center mb-24 relative">
          {/* Faint mark behind the hero */}
          <div className="absolute inset-0 flex items-start justify-center pointer-events-none -z-0 opacity-[0.06]">
            <MarkA size={420} color="var(--brand)" accent="var(--accent)" />
          </div>

          <div className="relative z-10">
            <div className="meta-label mb-4">Cover</div>
            <span className="badge bg-white text-biolab-700 border border-biolab-200 mb-6">
              <ShieldCheck className="h-3 w-3" />
              Biomedicina · Projeto acadêmico
            </span>
            <h1
              className="text-serif text-5xl sm:text-6xl text-biolab-700 leading-[1.05] mb-4"
              style={{ letterSpacing: "-0.01em" }}
            >
              Compatibilidade química,
              <br />
              em segundos.
            </h1>
            <p className="text-base text-biolab-900/75 max-w-xl mx-auto mb-9 leading-relaxed">
              Consulte substâncias e verifique se combinações são seguras.
              <br />
              Com base em FISPQ, GHS e normas regulamentadoras.
            </p>
            <div className="flex justify-center gap-3">
              <Link href="/register" className="btn-primary">
                Começar agora <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/login" className="btn-secondary">Já tenho conta</Link>
            </div>
          </div>
        </section>

        <div className="hairline mb-12" />

        <section>
          <div className="meta-label mb-3">O que faz</div>
          <h2
            className="text-serif text-3xl text-biolab-700 mb-8"
            style={{ letterSpacing: "-0.01em" }}
          >
            Três funções principais.
          </h2>

          <div className="grid sm:grid-cols-3 gap-5">
            <FeatureCard
              code="A · Catálogo"
              icon={Beaker}
              title="Catálogo de substâncias"
              text="Propriedades, riscos GHS e EPIs recomendados de cada reagente."
            />
            <FeatureCard
              code="B · Verificador"
              icon={FlaskConical}
              title="Verificação de pares"
              text="Selecione duas ou mais substâncias e veja o risco da combinação."
            />
            <FeatureCard
              code="C · Motor"
              icon={Database}
              title="Regras determinísticas"
              text="Veredicto rastreável, baseado em normas oficiais."
            />
          </div>
        </section>

        <div className="hairline my-16" />

        <section className="text-center">
          <div className="meta-label mb-2">Equipe</div>
          <p className="text-serif text-2xl text-biolab-700 leading-snug" style={{ letterSpacing: "-0.01em" }}>
            Desenvolvido por Vitória Silva Gobbis,
            <br className="hidden sm:block" />
            {" "}Natsumi Naruzawa, Carol Badin e Julia Blasius.
          </p>
        </section>

        <div className="hairline my-16" />

        <p className="text-center text-mono text-[10px] tracking-[0.16em] uppercase text-biolab-900/55">
          Ferramenta educacional · Não substitui FISPQ, GHS, NR ou supervisor de laboratório.
        </p>
      </main>
    </div>
  );
}

function FeatureCard({
  code,
  icon: Icon,
  title,
  text,
}: {
  code: string;
  icon: any;
  title: string;
  text: string;
}) {
  return (
    <div className="card p-6 relative">
      <div className="meta-label mb-4">{code}</div>
      <div className="h-10 w-10 rounded bg-biolab-300/40 text-biolab-500 grid place-items-center mb-4 border border-biolab-300/60">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="font-display font-semibold text-biolab-900 mb-2 text-lg" style={{ letterSpacing: "-0.01em" }}>
        {title}
      </h3>
      <p className="text-sm text-biolab-900/75 leading-relaxed">{text}</p>
    </div>
  );
}
