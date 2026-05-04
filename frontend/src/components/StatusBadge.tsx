import { CheckCircle2, AlertTriangle, ShieldAlert } from "lucide-react";
import type { RiskStatus } from "@/lib/types";

const VARIANTS: Record<RiskStatus, { label: string; className: string; Icon: any; code: string }> = {
  safe:    { label: "Seguro",       code: "LVL 01 / SAFE",     className: "badge-safe",    Icon: CheckCircle2 },
  unknown: { label: "Desconhecido", code: "LVL 02 / UNKNOWN",  className: "badge-unknown", Icon: AlertTriangle },
  unsafe:  { label: "Não seguro",   code: "LVL 03 / UNSAFE",   className: "badge-unsafe",  Icon: ShieldAlert },
};

export default function StatusBadge({ status }: { status: RiskStatus }) {
  const v = VARIANTS[status];
  const Icon = v.Icon;
  return (
    <span className={`badge ${v.className}`} title={v.code}>
      <Icon className="h-3 w-3" />
      {v.label}
    </span>
  );
}
