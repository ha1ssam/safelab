"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut, Beaker, FlaskConical, Shield } from "lucide-react";
import { useAuth } from "@/lib/auth";
import Logo from "./Logo";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Substâncias",              icon: Beaker },
  { href: "/check",     label: "Verificar compatibilidade", icon: FlaskConical },
  { href: "/hazards",   label: "Riscos (GHS)",              icon: Shield },
];

export default function Navbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <header className="border-b border-biolab-200 bg-[color:var(--paper)]/85 backdrop-blur sticky top-0 z-30">
      <div className="max-w-6xl mx-auto px-5 h-14 flex items-center gap-6">
        {/* Logo points to /dashboard while authenticated so clicking it
            never sends the user back to the marketing landing page. */}
        <Logo size="sm" href="/dashboard" caption={false} />

        <nav className="flex-1 flex items-center justify-center gap-1">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-2 px-3 py-2 rounded-sm text-sm font-medium transition border
                  ${active
                    ? "bg-biolab-300/40 text-biolab-700 border-biolab-300"
                    : "text-biolab-900/70 hover:bg-biolab-100/70 border-transparent"}`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          {user && (
            <div className="hidden sm:flex flex-col items-end leading-tight">
              <span className="text-sm font-medium text-biolab-900">
                {user.first_name || user.email}
              </span>
              <span className="text-mono text-[9px] tracking-[0.16em] uppercase text-biolab-900/55">
                {user.role_display}
              </span>
            </div>
          )}
          <button
            onClick={logout}
            className="btn-ghost border border-transparent hover:border-biolab-200"
            title="Sair"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
