import Link from "next/link";
import { useId } from "react";

interface MarkProps {
  size?: number;
  color?: string;
  accent?: string;
  className?: string;
}

/**
 * SafeLab MarkA — Frasco Molecular.
 * Geometric flask framed by a chemistry hexagon, with a molecular node on
 * top. Atomic orbits suggest analysis; the crosshair anchors precision.
 */
export function MarkA({
  size = 28,
  color = "currentColor",
  accent = "#d4a24a",
  className,
}: MarkProps) {
  const uid = useId().replace(/[:]/g, "");
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden
    >
      <defs>
        <clipPath id={`flask-${uid}`}>
          <path d="M50 50 L50 64 L36 90 Q33 98 41 98 L79 98 Q87 98 84 90 L70 64 L70 50 Z" />
        </clipPath>
        <linearGradient id={`liquid-${uid}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.35" />
          <stop offset="100%" stopColor={color} stopOpacity="0.7" />
        </linearGradient>
      </defs>

      {/* Atomic orbits */}
      <g opacity="0.55">
        <ellipse cx="60" cy="60" rx="54" ry="22" stroke={color} strokeWidth="1" fill="none" />
        <ellipse cx="60" cy="60" rx="54" ry="22" stroke={color} strokeWidth="1" fill="none" transform="rotate(60 60 60)" />
        <ellipse cx="60" cy="60" rx="54" ry="22" stroke={color} strokeWidth="1" fill="none" transform="rotate(-60 60 60)" />
      </g>

      {/* Hexagon frame */}
      <path
        d="M60 12 L98 34 L98 78 L60 100 L22 78 L22 34 Z"
        stroke={color}
        strokeWidth="1.5"
        fill="none"
        opacity="0.35"
        strokeDasharray="2 3"
      />
      {[
        [60, 12], [98, 34], [98, 78], [60, 100], [22, 78], [22, 34],
      ].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="1.5" fill={color} opacity="0.5" />
      ))}

      {/* Measurement ticks */}
      <g stroke={color} strokeWidth="0.8" opacity="0.4">
        <line x1="32" y1="72" x2="35" y2="72" />
        <line x1="32" y1="80" x2="35" y2="80" />
        <line x1="32" y1="88" x2="35" y2="88" />
      </g>

      {/* Flask body */}
      <path
        d="M50 50 L50 64 L36 90 Q33 98 41 98 L79 98 Q87 98 84 90 L70 64 L70 50 Z"
        fill="white"
        fillOpacity="0.4"
        stroke={color}
        strokeWidth="2.5"
        strokeLinejoin="round"
      />

      {/* Liquid */}
      <g clipPath={`url(#flask-${uid})`}>
        <rect x="30" y="76" width="60" height="30" fill={`url(#liquid-${uid})`} />
        <path d="M30 76 Q40 72 50 76 T70 76 T90 76 L90 80 L30 80 Z" fill={color} fillOpacity="0.25" />
        <path d="M30 76 Q40 72 50 76 T70 76 T90 76" stroke={color} strokeWidth="1.2" fill="none" opacity="0.6" />
        <circle cx="46" cy="86" r="1.2" fill={color} fillOpacity="0.4" />
        <circle cx="58" cy="92" r="0.8" fill={color} fillOpacity="0.4" />
        <circle cx="68" cy="84" r="1" fill={color} fillOpacity="0.4" />
        <circle cx="52" cy="94" r="0.7" fill={color} fillOpacity="0.4" />
      </g>

      {/* Neck */}
      <line x1="48" y1="50" x2="72" y2="50" stroke={color} strokeWidth="2.5" strokeLinecap="round" />
      <line x1="50" y1="54" x2="70" y2="54" stroke={color} strokeWidth="1" opacity="0.5" />

      {/* Molecular structure above */}
      <g stroke={color} strokeWidth="1.8">
        <line x1="60" y1="44" x2="42" y2="30" />
        <line x1="60" y1="44" x2="78" y2="30" />
        <line x1="42" y1="30" x2="60" y2="20" />
        <line x1="78" y1="30" x2="60" y2="20" />
        <line x1="44" y1="32" x2="58" y2="22" strokeWidth="0.8" opacity="0.6" />
      </g>
      <circle cx="60" cy="44" r="4" fill={color} />
      <circle cx="60" cy="44" r="1.8" fill="white" opacity="0.6" />
      <circle cx="42" cy="30" r="4" fill={color} stroke={accent} strokeWidth="1.5" />
      <circle cx="78" cy="30" r="4" fill={color} stroke={accent} strokeWidth="1.5" />
      <circle cx="60" cy="20" r="3.5" fill={accent} />
      <circle cx="60" cy="20" r="1.2" fill={color} />

      {/* Crosshair */}
      <g opacity="0.5">
        <circle cx="60" cy="98" r="3" stroke={accent} strokeWidth="1" fill="none" />
        <line x1="56" y1="98" x2="58" y2="98" stroke={accent} strokeWidth="1" />
        <line x1="62" y1="98" x2="64" y2="98" stroke={accent} strokeWidth="1" />
      </g>
    </svg>
  );
}

/**
 * SafeLab wordmark + mark, in three sizes. Matches the identity canvas:
 * "Safe" (semibold, brand) + "Lab" (regular, ink) + tiny mono caption.
 *
 * `href` defaults to "/" but should be set to "/dashboard" when rendered
 * inside the authenticated app shell — clicking the logo while signed in
 * should never bounce the user back to the marketing page (which would
 * appear to "log them out" since /login redirects come from auth state).
 */
export default function Logo({
  size = "md",
  href = "/",
  caption,
}: {
  size?: "sm" | "md" | "lg";
  href?: string;
  caption?: boolean;
}) {
  const cfg = {
    sm: { mark: 26, word: "text-lg",  caption: false },
    md: { mark: 32, word: "text-xl",  caption: true  },
    lg: { mark: 44, word: "text-3xl", caption: true  },
  }[size];
  const showCaption = caption ?? cfg.caption;

  return (
    <Link href={href} className="flex items-center gap-2.5 select-none group">
      <MarkA size={cfg.mark} color="var(--brand)" accent="var(--accent)" />
      <div className="flex flex-col leading-none">
        <span
          className={`${cfg.word} font-display font-semibold tracking-tight text-biolab-500`}
          style={{ letterSpacing: "-0.025em" }}
        >
          Safe<span className="font-normal text-biolab-900">Lab</span>
        </span>
        {showCaption && (
          <span className="text-mono text-[9px] tracking-[0.18em] uppercase text-biolab-900/50 mt-1">
            Análise de interações
          </span>
        )}
      </div>
    </Link>
  );
}
