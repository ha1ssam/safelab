"""
Compatibility — Service layer.
Orchestrates the compatibility check pipeline:

    1. Look up curated CompatibilityRecord(s) in the DB.
    2. Evaluate the deterministic rules engine.
    3. Consolidate findings — always returning the *worst* verdict.
    4. If nothing applies anywhere, fall back to "unknown" with an alert.

This module is the only entry point that views/CLI/tests should use to perform
a check — keep all business logic here, never in the views.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Iterable

from substances.models import Substance

from .models import CompatibilityRecord
from .rules import (
    RuleFinding,
    consolidate,
    evaluate_rules,
    STATUS_SAFE,
    STATUS_UNKNOWN,
    STATUS_UNSAFE,
    RISK_LOW,
    RISK_MEDIUM,
)


# ─── Result shapes ────────────────────────────────────────────────────────────

@dataclass
class PairResult:
    """Result of evaluating a single pair (a, b)."""

    substance_a_id: int
    substance_b_id: int
    substance_a_name: str
    substance_b_name: str
    status: str  # safe | unsafe | unknown
    risk_level: str  # low | medium | high
    reaction_type: str = ""
    message: str = ""
    sources: list[str] = field(default_factory=list)  # which layers contributed
    findings: list[dict] = field(default_factory=list)  # rule-level details
    record_id: int | None = None  # curated record, when present

    def as_dict(self) -> dict:
        return {
            "substance_a_id": self.substance_a_id,
            "substance_b_id": self.substance_b_id,
            "substance_a_name": self.substance_a_name,
            "substance_b_name": self.substance_b_name,
            "status": self.status,
            "risk_level": self.risk_level,
            "reaction_type": self.reaction_type,
            "message": self.message,
            "sources": self.sources,
            "findings": self.findings,
            "record_id": self.record_id,
        }


@dataclass
class CheckResult:
    """Result of evaluating a list of substances (all pair combinations)."""

    overall_status: str
    overall_risk: str
    overall_message: str
    pairs: list[PairResult]
    required_ppe: list[str] = field(default_factory=list)
    critical_alerts: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "overall_status": self.overall_status,
            "overall_risk": self.overall_risk,
            "overall_message": self.overall_message,
            "required_ppe": self.required_ppe,
            "critical_alerts": self.critical_alerts,
            "pairs": [p.as_dict() for p in self.pairs],
        }


# ─── Internal helpers ─────────────────────────────────────────────────────────

_STATUS_RANK = {STATUS_SAFE: 0, STATUS_UNKNOWN: 1, STATUS_UNSAFE: 2}
_RISK_RANK = {"low": 0, "medium": 1, "high": 2}

_OVERALL_MESSAGES = {
    STATUS_SAFE: "Nenhuma incompatibilidade conhecida entre as substâncias selecionadas.",
    STATUS_UNKNOWN: "Atenção: dados insuficientes para garantir segurança em pelo menos uma combinação.",
    STATUS_UNSAFE: "ALERTA: combinação(ões) com risco identificado. Não manipular sem revisão.",
}


def _findings_to_dicts(findings: list[RuleFinding]) -> list[dict]:
    return [
        {
            "rule_id": f.rule_id,
            "status": f.status,
            "risk_level": f.risk_level,
            "reaction_type": f.reaction_type,
            "message": f.message,
            "notes": f.notes,
        }
        for f in findings
    ]


def _evaluate_pair(a: Substance, b: Substance) -> PairResult:
    """
    Evaluate a single ordered pair. The flow is:
      1. Curated record (if any) seeds the verdict.
      2. Rules engine adds further findings (and may upgrade the risk).
      3. Final verdict = worst across whichever layers actually contributed.
         (We do NOT mix in the default "unknown" of an empty layer.)
    """
    # Always normalize so the lookup matches the normalized DB row.
    s1, s2 = (a, b) if a.id < b.id else (b, a)

    sources: list[str] = []
    record_id: int | None = None
    record_reaction = ""
    record_message = ""

    record = CompatibilityRecord.objects.filter(
        substance_a=s1, substance_b=s2
    ).first()

    rule_findings = evaluate_rules(s1, s2)
    if rule_findings:
        sources.append("rules")
    if record:
        sources.append("record")
        record_id = record.id
        record_reaction = record.reaction_type
        record_message = record.notes

    # Build a candidate list of (status, risk) from layers that actually fired.
    candidates: list[tuple[str, str]] = []
    if record:
        candidates.append((record.status, record.risk_level))
    if rule_findings:
        candidates.append(consolidate(rule_findings))

    if candidates:
        final_status = max((c[0] for c in candidates), key=lambda s: _STATUS_RANK[s])
        final_risk = max((c[1] for c in candidates), key=lambda r: _RISK_RANK[r])
    else:
        final_status, final_risk = STATUS_UNKNOWN, RISK_LOW

    # Pick a primary message: prefer the most severe rule finding, else record notes.
    message = record_message
    reaction_type = record_reaction
    if rule_findings:
        worst = max(rule_findings, key=lambda f: (_STATUS_RANK[f.status], _RISK_RANK[f.risk_level]))
        if worst.message:
            message = worst.message
        if worst.reaction_type and not reaction_type:
            reaction_type = worst.reaction_type

    if not sources:
        # Neither curated nor any rule fired → unknown by safety policy.
        sources.append("fallback_unknown")
        message = (
            f"Sem regra específica nem registro curado para {s1.name} + {s2.name}. "
            "Consulte a FISPQ Seção 10 (Estabilidade e Reatividade) e a "
            "Seção 7 (Manuseio e Armazenamento) de cada substância antes de "
            "manipular. Referências: ABNT NBR 14725, GHS Rev. 9, NR-26."
        )
        final_status = STATUS_UNKNOWN
        final_risk = max([final_risk, RISK_MEDIUM], key=lambda r: _RISK_RANK[r])

    return PairResult(
        substance_a_id=s1.id,
        substance_b_id=s2.id,
        substance_a_name=s1.name,
        substance_b_name=s2.name,
        status=final_status,
        risk_level=final_risk,
        reaction_type=reaction_type,
        message=message,
        sources=sources,
        findings=_findings_to_dicts(rule_findings),
        record_id=record_id,
    )


# ─── Public API ───────────────────────────────────────────────────────────────

def check_compatibility(substance_ids: Iterable[int]) -> CheckResult:
    """
    Evaluate compatibility across an arbitrary list of substance IDs.
    Generates one PairResult per unordered pair; consolidates an overall verdict.

    Raises ValueError when fewer than 2 IDs are supplied.
    """
    ids = list(dict.fromkeys(int(x) for x in substance_ids))  # dedupe, preserve order
    if len(ids) < 2:
        raise ValueError("São necessárias pelo menos 2 substâncias para checar compatibilidade.")

    substances = list(
        Substance.objects.prefetch_related("hazards").filter(id__in=ids)
    )
    by_id = {s.id: s for s in substances}

    missing = [i for i in ids if i not in by_id]
    if missing:
        raise ValueError(f"Substância(s) não encontrada(s): {missing}")

    pairs: list[PairResult] = []
    for a, b in combinations([by_id[i] for i in ids], 2):
        pairs.append(_evaluate_pair(a, b))

    # Consolidate overall verdict (worst across all pairs).
    if pairs:
        overall_status = max((p.status for p in pairs), key=lambda s: _STATUS_RANK[s])
        overall_risk = max((p.risk_level for p in pairs), key=lambda r: _RISK_RANK[r])
    else:
        overall_status, overall_risk = STATUS_UNKNOWN, RISK_LOW

    # Aggregate handling info from each substance's profile.
    ppe_set: list[str] = []
    seen_ppe = set()
    alerts: list[str] = []
    for s in substances:
        for item in (s.required_ppe or []):
            if item not in seen_ppe:
                seen_ppe.add(item)
                ppe_set.append(item)
        if s.critical_alerts:
            alerts.append(f"{s.name}: {s.critical_alerts}")

    return CheckResult(
        overall_status=overall_status,
        overall_risk=overall_risk,
        overall_message=_OVERALL_MESSAGES[overall_status],
        pairs=pairs,
        required_ppe=ppe_set,
        critical_alerts=alerts,
    )
