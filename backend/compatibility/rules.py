"""
Compatibility — Rules Engine.

Deterministic, data-driven rules that infer compatibility between two
substances based on their stored properties (acid/base/water/organic flags
and hazard codes).

Design notes
────────────
- The engine NEVER uses AI / LLMs at runtime. All decisions are a pure function
  of the substance attributes that the seed data + admin UI populate.
- Each rule is a tiny pure function `(a, b) -> Optional[RuleFinding]`.
- A rule returns `None` when it does not apply, or a `RuleFinding` describing
  what it found. Rules are *symmetric* — they must check both orderings of the
  pair (helper `_either` does this).
- Rules are NEVER allowed to upgrade an `unsafe` finding to `safe`. The final
  status is the *worst* status reported by any rule.
- If no rule fires AND there is no curated `CompatibilityRecord`, the engine
  reports `unknown` with an explicit "missing data" alert (per the project's
  safety policy: never assume safety without evidence).

Adding a new rule
─────────────────
1. Write a function `def rule_<name>(a, b) -> Optional[RuleFinding]`.
2. Append it to `RULES` at the bottom of this module.
The motor will call it for every pair check.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

from substances.models import Substance


# ─── Status / risk constants (kept as plain strings to avoid coupling to ORM) ──
STATUS_SAFE = "safe"
STATUS_UNSAFE = "unsafe"
STATUS_UNKNOWN = "unknown"

RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"

_STATUS_RANK = {STATUS_SAFE: 0, STATUS_UNKNOWN: 1, STATUS_UNSAFE: 2}
_RISK_RANK = {RISK_LOW: 0, RISK_MEDIUM: 1, RISK_HIGH: 2}


@dataclass
class RuleFinding:
    """A single rule's verdict on a pair."""

    rule_id: str
    status: str  # safe | unsafe | unknown
    risk_level: str  # low | medium | high
    reaction_type: str = ""
    message: str = ""
    notes: list[str] = field(default_factory=list)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _either(a: Substance, b: Substance, predicate_a, predicate_b) -> bool:
    """
    Returns True if `(predicate_a(a) and predicate_b(b))` OR
                   `(predicate_a(b) and predicate_b(a))` — i.e., the pair
    matches the predicate in either ordering. Lets us write rules without
    worrying about argument order.
    """
    return (predicate_a(a) and predicate_b(b)) or (predicate_a(b) and predicate_b(a))


def _has_hazard(s: Substance, code: str) -> bool:
    return code in s.hazard_codes


# ─── Individual rules ─────────────────────────────────────────────────────────
# Each rule returns a RuleFinding when it applies, otherwise None.

def rule_acid_plus_water(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Strong acid + water: can be safely diluted ONLY if the acid is added to
    the water — never the reverse (risk of violent splash and exothermic boiling).
    Issue an explicit advisory rather than blocking the pair.
    """
    if _either(a, b, lambda s: s.is_acid, lambda s: s.is_water):
        return RuleFinding(
            rule_id="acid_plus_water",
            status=STATUS_SAFE,
            risk_level=RISK_MEDIUM,
            reaction_type="Diluição exotérmica",
            message="Adicione SEMPRE o ácido na água, NUNCA o contrário.",
            notes=[
                "A diluição é exotérmica — adicionar água ao ácido pode gerar respingos e ebulição violenta.",
                "Faça em pequenas porções, com agitação, em recipiente resistente.",
            ],
        )
    return None


def rule_acid_plus_base(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """Acid + base: neutralization, exothermic. Risk depends on concentration."""
    if _either(a, b, lambda s: s.is_acid, lambda s: s.is_base):
        # Skip if water is involved — handled by rule_acid_plus_water.
        if a.is_water or b.is_water:
            return None
        return RuleFinding(
            rule_id="acid_plus_base",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Neutralização exotérmica",
            message="Reação ácido-base fortemente exotérmica — risco de respingos e calor intenso.",
            notes=[
                "Manipule sob exaustão e com EPIs completos.",
                "Não misture quantidades estequiométricas sem diluição prévia.",
            ],
        )
    return None


def rule_oxidizer_plus_flammable(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """Oxidizer + flammable: classic fire / explosion combination."""
    if _either(
        a, b,
        lambda s: _has_hazard(s, "oxidizer"),
        lambda s: _has_hazard(s, "flammable") or s.is_organic_solvent,
    ):
        return RuleFinding(
            rule_id="oxidizer_plus_flammable",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Risco de combustão / explosão",
            message="Oxidante em contato com material inflamável — risco severo de ignição.",
            notes=[
                "Mantenha em armários separados.",
                "Nunca manuseie próximo a fontes de calor ou faísca.",
            ],
        )
    return None


def rule_oxidizer_plus_organic(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """Oxidizer + organic solvent (catch-all that complements the previous rule)."""
    if _either(
        a, b,
        lambda s: _has_hazard(s, "oxidizer"),
        lambda s: s.is_organic_solvent,
    ):
        return RuleFinding(
            rule_id="oxidizer_plus_organic",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Reação oxidativa violenta",
            message="Oxidantes fortes podem reagir violentamente com solventes orgânicos.",
        )
    return None


def rule_oxidizer_plus_oxidizer(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Two oxidizers together: many specific combinations are dangerous (e.g.
    H2O2 + KMnO4 → decomposição violenta de O2; HNO3 + KClO3 → instável).
    Generic advisory of HIGH risk per OSHA/NFPA segregation tables.
    """
    if _has_hazard(a, "oxidizer") and _has_hazard(b, "oxidizer"):
        return RuleFinding(
            rule_id="oxidizer_plus_oxidizer",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Combinação de oxidantes",
            message=(
                "Dois oxidantes fortes — muitas combinações geram decomposição "
                "violenta com liberação de O2 e calor (ex: H2O2 + KMnO4)."
            ),
            notes=[
                "Armazenar separadamente (NFPA 430 / NR-26).",
                "Consulte FISPQ Seção 10 da combinação específica.",
            ],
        )
    return None


def rule_oxidizer_plus_acid(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Strong acid + oxidizer (esp. permanganato, clorato, dicromato) — risco
    de formação de óxidos instáveis (ex: H2SO4 + KMnO4 → Mn2O7 explosivo).
    """
    if _either(
        a, b,
        lambda s: s.is_acid or _has_hazard(s, "corrosive"),
        lambda s: _has_hazard(s, "oxidizer"),
    ):
        # Skip if both are oxidizers (handled by rule_oxidizer_plus_oxidizer)
        if _has_hazard(a, "oxidizer") and _has_hazard(b, "oxidizer"):
            return None
        return RuleFinding(
            rule_id="oxidizer_plus_acid",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Formação de óxidos instáveis",
            message=(
                "Ácido forte + oxidante: pode gerar óxidos altamente reativos "
                "ou explosivos (ex: H2SO4 + KMnO4 → Mn2O7 explosivo a 55°C)."
            ),
            notes=["Referência: Bretherick's Handbook of Reactive Chemical Hazards."],
        )
    return None


def rule_oxidizer_plus_organic_compound(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Strong oxidizer (KMnO4, K2Cr2O7, HNO3, NaClO3, H2O2 conc., etc.) in contact
    with any organic compound (carbono na fórmula) — combustão/ignição.

    Catches cases the existing oxidizer_plus_organic misses: KMnO4 + glicerol,
    KMnO4 + sacarose, HNO3 + papel/algodão. Glicerol/sacarose não são
    'is_organic_solvent' mas têm carbono e queimam quando oxidados.
    """
    def has_carbon(s: Substance) -> bool:
        f = (s.formula or "").strip()
        return bool(f) and "C" in f and not f.startswith("Ca") and not f.startswith("Co") and not f.startswith("Cu") and not f.startswith("Cl") and not f.startswith("Cr") and not f.startswith("Cs") and not f.startswith("Cd")

    if _either(
        a, b,
        lambda s: _has_hazard(s, "oxidizer"),
        lambda s: has_carbon(s) and not _has_hazard(s, "oxidizer"),
    ):
        # Avoid double-firing with rule_oxidizer_plus_organic (organic solvent).
        if a.is_organic_solvent or b.is_organic_solvent:
            return None
        return RuleFinding(
            rule_id="oxidizer_plus_organic_compound",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Oxidação de composto orgânico",
            message=(
                "Oxidante forte em contato com composto orgânico (ex: glicerol, "
                "açúcar, papel) pode causar ignição espontânea — reação altamente "
                "exotérmica."
            ),
            notes=[
                "Caso clássico: KMnO4 + glicerol → ignição em segundos.",
                "Referência: NFPA 430 / FISPQ Seção 10.",
            ],
        )
    return None


def rule_water_reactive_plus_water(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """A substance flagged as 'reage com água' should never contact water."""
    # Skip if the "water-reactive" substance is actually an acid: its dilution
    # is exothermic but not dangerous when added correctly. rule_acid_plus_water
    # already provides the right advisory for that case.
    if _either(
        a, b,
        lambda s: _has_hazard(s, "reactive_water") and not s.is_acid,
        lambda s: s.is_water,
    ):
        return RuleFinding(
            rule_id="water_reactive_plus_water",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Reação violenta com água",
            message="Substância reativa com água — pode liberar gases inflamáveis ou tóxicos.",
            notes=[
                "Armazene em ambiente seco e selado.",
                "Em caso de derramamento, NÃO usar água — siga o protocolo específico.",
            ],
        )
    return None


def rule_toxic_pair_advisory(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Two toxic substances together: increases exposure risk but is not a
    chemical incompatibility per se. Treat as SAFE with a medium-risk handling
    advisory — the user should still combine in a fume hood with full PPE.
    """
    if _has_hazard(a, "toxic") and _has_hazard(b, "toxic"):
        return RuleFinding(
            rule_id="toxic_pair_advisory",
            status=STATUS_SAFE,
            risk_level=RISK_MEDIUM,
            reaction_type="Atenção: exposição cumulativa",
            message=(
                "Ambas substâncias têm classificação tóxica (GHS H300–H373). "
                "Sem incompatibilidade química direta, mas manuseie em capela "
                "com EPIs completos."
            ),
            notes=["Referência: FISPQ Seção 8 (Controle de exposição / EPIs)."],
        )
    return None


def rule_corrosive_pair(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """Two corrosives in contact: assume reactive unless explicitly recorded as safe."""
    if _has_hazard(a, "corrosive") and _has_hazard(b, "corrosive"):
        # Same-class corrosives (acid+acid or base+base) are usually compatible
        # for storage but still require segregation per NR-26 / ABNT NBR 14725.
        if (a.is_acid and b.is_acid) or (a.is_base and b.is_base):
            return RuleFinding(
                rule_id="corrosive_same_class",
                status=STATUS_SAFE,
                risk_level=RISK_LOW,
                reaction_type="Mesma classe corrosiva",
                message=(
                    "Corrosivos de mesma classe — compatíveis quimicamente, "
                    "mas devem ser segregados por concentração (NR-26 / ABNT 14725)."
                ),
            )
        return None  # acid+base case is handled by rule_acid_plus_base
    return None


def rule_explosive_with_anything(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Explosives / self-reactive / organic peroxides require dedicated storage
    and never share storage with other hazardous classes (NR-19, NR-26).
    """
    if _has_hazard(a, "explosive") or _has_hazard(b, "explosive"):
        return RuleFinding(
            rule_id="explosive_segregation",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Substância explosiva / auto-reativa",
            message=(
                "Substâncias explosivas, auto-reativas ou peróxidos orgânicos "
                "exigem armazenamento dedicado — não podem compartilhar área "
                "com outras classes (NR-19, NR-26, GHS H200–H205, H240–H242)."
            ),
            notes=[
                "Manter em local frio, ventilado e longe de fontes de ignição.",
                "Consulte a FISPQ Seção 7 para condições específicas.",
            ],
        )
    return None


def rule_corrosive_plus_metal(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Corrosives (especially acids) attack reactive metals → liberação de H2 (inflamável).
    This catches generic acid/corrosive + metal pairs.
    """
    metal_keywords = ("metálico", "metalico", "em pó", "em po", "em fita")

    def is_reactive_metal(s: Substance) -> bool:
        n = s.name.lower()
        return any(kw in n for kw in metal_keywords)

    if _either(
        a, b,
        lambda s: _has_hazard(s, "corrosive") or s.is_acid,
        is_reactive_metal,
    ):
        return RuleFinding(
            rule_id="corrosive_plus_metal",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Liberação de hidrogênio inflamável",
            message=(
                "Corrosivo / ácido em contato com metal reativo libera "
                "hidrogênio (H2), que é altamente inflamável."
            ),
            notes=[
                "Risco de explosão se houver fonte de ignição.",
                "Referência: FISPQ Seção 10 (estabilidade e reatividade).",
            ],
        )
    return None


def rule_cyanide_plus_acid(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Cyanide salts + any acid → cianeto de hidrogênio (HCN) gasoso, extremamente tóxico.
    Classic incompatibility per NIOSH / FISPQ.
    """
    def is_cyanide(s: Substance) -> bool:
        n = s.name.lower()
        return "cianeto" in n or "cyanide" in n

    if _either(a, b, is_cyanide, lambda s: s.is_acid or _has_hazard(s, "corrosive")):
        return RuleFinding(
            rule_id="cyanide_plus_acid",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Liberação de HCN (cianeto de hidrogênio)",
            message=(
                "Cianeto + ácido libera HCN gasoso — extremamente tóxico, "
                "letal mesmo em baixas concentrações."
            ),
            notes=[
                "Manuseie SOMENTE em capela com exaustão validada.",
                "Referência: NIOSH Pocket Guide / FISPQ Seção 10.",
            ],
        )
    return None


def rule_hypochlorite_plus_acid(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Hipoclorito + ácido → liberação de Cl2 gasoso (tóxico, irritante).
    """
    def is_hypochlorite(s: Substance) -> bool:
        n = s.name.lower()
        return "hipoclorito" in n or "hypochlorite" in n

    if _either(a, b, is_hypochlorite, lambda s: s.is_acid):
        return RuleFinding(
            rule_id="hypochlorite_plus_acid",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Liberação de cloro gasoso (Cl2)",
            message=(
                "Hipoclorito + ácido libera Cl2 gasoso — tóxico e corrosivo "
                "para vias respiratórias."
            ),
            notes=[
                "Use somente em capela; monitorar concentração de Cl2 no ar.",
                "Referência: FISPQ Seção 10 / OSHA 1910.1000.",
            ],
        )
    return None


def rule_hypochlorite_plus_ammonia(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Hipoclorito + amônia → cloramina (NH2Cl, NHCl2) tóxica/explosiva.
    Causa comum de acidentes domésticos e em hospitais (limpeza).
    """
    def is_hypochlorite(s: Substance) -> bool:
        n = s.name.lower()
        return "hipoclorito" in n or "hypochlorite" in n

    def is_ammonia(s: Substance) -> bool:
        n = s.name.lower()
        return n.startswith("amônia") or n.startswith("amonia") or "hidróxido de am" in n or "hidroxido de am" in n or "ammonia" in n

    if _either(a, b, is_hypochlorite, is_ammonia):
        return RuleFinding(
            rule_id="hypochlorite_plus_ammonia",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Formação de cloraminas tóxicas",
            message=(
                "Hipoclorito + amônia → cloraminas (NH2Cl, NHCl2) gasosas, "
                "altamente tóxicas e potencialmente explosivas."
            ),
            notes=[
                "Causa frequente de intoxicação em ambientes hospitalares.",
                "Referência: NIOSH / FISPQ Seção 10.",
            ],
        )
    return None


def rule_peroxide_plus_anything_organic(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Peróxido de hidrogênio (e outros peróxidos) + cetonas → peróxidos cíclicos
    explosivos (TATP, peróxido de acetona). Evento comum em laboratório.
    """
    def is_peroxide(s: Substance) -> bool:
        n = s.name.lower()
        return "peróxido" in n or "peroxido" in n or "peroxide" in n

    def is_ketone_or_aldehyde(s: Substance) -> bool:
        n = s.name.lower()
        return any(k in n for k in ("acetona", "cetona", "metiletilcetona", "mek", "aldeído", "aldeido", "formaldeído", "formaldeido"))

    if _either(a, b, is_peroxide, is_ketone_or_aldehyde):
        return RuleFinding(
            rule_id="peroxide_plus_ketone",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Formação de peróxidos cíclicos explosivos",
            message=(
                "Peróxido + cetona/aldeído pode formar peróxidos cíclicos "
                "altamente explosivos (ex: peróxido de acetona / TATP)."
            ),
            notes=[
                "Não armazene H2O2 próximo de acetona ou MEK.",
                "Referência: Bretherick's / OSHA SOP.",
            ],
        )
    return None


def rule_sulfide_plus_acid(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """Sulfetos + ácido → H2S gasoso (extremamente tóxico)."""
    def is_sulfide(s: Substance) -> bool:
        n = s.name.lower()
        return "sulfeto" in n or "sulfide" in n or "sulfito" in n

    if _either(a, b, is_sulfide, lambda s: s.is_acid):
        return RuleFinding(
            rule_id="sulfide_plus_acid",
            status=STATUS_UNSAFE,
            risk_level=RISK_HIGH,
            reaction_type="Liberação de H2S (gás sulfídrico)",
            message="Sulfeto/sulfito + ácido libera H2S — tóxico e inflamável.",
            notes=["Capela obrigatória; H2S deprime o nervo olfativo rapidamente."],
        )
    return None


def rule_inert_plus_inert(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    When both substances have no hazard codes at all and neither is acid/base/
    organic-solvent/oxidizer, treat as compatible. Examples: water + saline,
    sucrose + glycerol, two buffer salts.
    """
    inert_a = (
        not a.hazard_codes
        and not a.is_acid and not a.is_base
        and not a.is_organic_solvent
    )
    inert_b = (
        not b.hazard_codes
        and not b.is_acid and not b.is_base
        and not b.is_organic_solvent
    )
    if inert_a and inert_b:
        return RuleFinding(
            rule_id="inert_pair",
            status=STATUS_SAFE,
            risk_level=RISK_LOW,
            reaction_type="Compatível",
            message="Ambas substâncias sem riscos GHS reportados — combinação considerada segura.",
        )
    return None


def rule_low_hazard_pair(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Both substances have only low-severity hazard codes (irritant / env_hazard)
    and no reactive flags → safe combination per GHS H315/H319/H400 categories
    (skin/eye irritation and aquatic hazards alone don't drive incompatibility).
    """
    LOW_ONLY = {"irritant", "env_hazard"}

    def only_low_hazards(s: Substance) -> bool:
        codes = set(s.hazard_codes)
        if not codes:
            return False
        return codes.issubset(LOW_ONLY)

    inert_chemistry = lambda s: not (s.is_acid or s.is_base or s.is_organic_solvent)

    if (
        only_low_hazards(a) and only_low_hazards(b)
        and inert_chemistry(a) and inert_chemistry(b)
    ):
        return RuleFinding(
            rule_id="low_hazard_pair",
            status=STATUS_SAFE,
            risk_level=RISK_LOW,
            reaction_type="Compatível",
            message="Apenas riscos de irritação / ambientais — sem reatividade química esperada.",
        )
    return None


def rule_non_reactive_pair(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Catch-all SAFE rule: when BOTH sides are chemically inert (no acid/base/
    organic-solvent/water-reactive/oxidizer/explosive/flammable flag and no
    such hazard code), no reaction can occur.

    IMPORTANT: requires *both* sides to be inert. A single reactive substance
    paired with an "inert salt" is NOT automatically safe — the salt may still
    react (e.g. KMnO4 oxidizes a sugar, H2SO4 dehydrates a carbohydrate). Only
    when neither side has any reactive functional group can we be confident.

    Hazards like toxic / carcinogen / irritant / env_hazard are *exposure*
    risks, not *reactivity* risks. Cumulative exposure is reported elsewhere.
    """
    REACTIVE_HAZARDS = {
        "oxidizer", "reactive_water", "explosive", "compressed_gas", "flammable",
    }

    def is_chemically_reactive(s: Substance) -> bool:
        if s.is_acid or s.is_base or s.is_water or s.is_organic_solvent:
            return True
        return bool(set(s.hazard_codes) & REACTIVE_HAZARDS)

    if is_chemically_reactive(a) or is_chemically_reactive(b):
        return None

    return RuleFinding(
        rule_id="non_reactive_pair",
        status=STATUS_SAFE,
        risk_level=RISK_LOW,
        reaction_type="Sem reatividade química esperada",
        message=(
            "Nenhuma das substâncias possui grupo funcional reativo "
            "(ácido/base/oxidante/inflamável/reativo com água) — combinação "
            "considerada segura. Hazards individuais ainda devem ser observados."
        ),
        notes=["Referência: GHS Rev. 9 / FISPQ Seção 10."],
    )


def rule_organic_pair(a: Substance, b: Substance) -> Optional[RuleFinding]:
    """
    Two organic solvents (neither oxidizer): generally miscible / compatible
    for handling. Still alert about cumulative flammability if both flammable.
    """
    if a.is_organic_solvent and b.is_organic_solvent:
        if _has_hazard(a, "oxidizer") or _has_hazard(b, "oxidizer"):
            return None  # handled by rule_oxidizer_plus_organic
        both_flammable = _has_hazard(a, "flammable") and _has_hazard(b, "flammable")
        return RuleFinding(
            rule_id="organic_pair",
            status=STATUS_SAFE,
            risk_level=RISK_MEDIUM if both_flammable else RISK_LOW,
            reaction_type="Solventes orgânicos compatíveis",
            message=(
                "Solventes orgânicos sem oxidante — geralmente compatíveis. "
                + ("Mantenha distância de fontes de ignição (ambos inflamáveis)." if both_flammable else "")
            ).strip(),
        )
    return None


# ─── Rule registry ────────────────────────────────────────────────────────────

RuleFn = Callable[[Substance, Substance], Optional[RuleFinding]]

RULES: Sequence[RuleFn] = (
    # — Specific high-risk reactions (must come first to lock in the verdict)
    rule_cyanide_plus_acid,
    rule_hypochlorite_plus_acid,
    rule_hypochlorite_plus_ammonia,
    rule_sulfide_plus_acid,
    rule_peroxide_plus_anything_organic,
    rule_explosive_with_anything,
    # — Oxidizer combinations (high priority — cover dangerous oxidizer pairings)
    rule_oxidizer_plus_oxidizer,
    rule_oxidizer_plus_acid,
    rule_oxidizer_plus_flammable,
    rule_oxidizer_plus_organic,
    rule_oxidizer_plus_organic_compound,
    # — General reactivity classes
    rule_acid_plus_water,
    rule_acid_plus_base,
    rule_water_reactive_plus_water,
    rule_corrosive_plus_metal,
    rule_corrosive_pair,
    # — Advisory + safe-pair detection (provide explicit verdicts to avoid "unknown")
    rule_toxic_pair_advisory,
    rule_organic_pair,
    rule_low_hazard_pair,
    rule_inert_plus_inert,
    rule_non_reactive_pair,  # broadest catch-all SAFE rule, evaluated last
)


def evaluate_rules(a: Substance, b: Substance) -> list[RuleFinding]:
    """Run every rule against the pair and return all findings (in declaration order)."""
    findings: list[RuleFinding] = []
    for fn in RULES:
        finding = fn(a, b)
        if finding is not None:
            findings.append(finding)
    return findings


def consolidate(findings: Sequence[RuleFinding]) -> tuple[str, str]:
    """
    Reduce a list of findings to a single (status, risk_level).
    Always returns the *worst* status and the *highest* risk seen.
    """
    if not findings:
        return STATUS_UNKNOWN, RISK_LOW
    status = max((f.status for f in findings), key=lambda s: _STATUS_RANK[s])
    risk = max((f.risk_level for f in findings), key=lambda r: _RISK_RANK[r])
    return status, risk
