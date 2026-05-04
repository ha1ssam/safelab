"""
Substances app — Models.
A Substance is a chemical reagent with physical/chemical properties, hazard tags,
PPE recommendations and storage guidance. Storing properties as discrete boolean
flags (instead of free text) lets the rules engine reason over them deterministically.
"""

from django.db import models
from hazards.models import Hazard


class Substance(models.Model):
    """A chemical substance/reagent catalog entry."""

    class PhysicalState(models.TextChoices):
        SOLID = "solid", "Sólido"
        LIQUID = "liquid", "Líquido"
        GAS = "gas", "Gás"
        AQUEOUS = "aqueous", "Solução aquosa"

    # ─── Identification ─────────────────────────────────────────────────────
    name = models.CharField("Nome", max_length=120, unique=True)
    formula = models.CharField("Fórmula química", max_length=80, blank=True)
    cas_number = models.CharField(
        "Número CAS",
        max_length=20,
        blank=True,
        help_text="Chemical Abstracts Service registry number (ex: 7647-01-0).",
    )
    description = models.TextField("Descrição", blank=True)

    # ─── Physical properties ───────────────────────────────────────────────
    physical_state = models.CharField(
        "Estado físico",
        max_length=10,
        choices=PhysicalState.choices,
        default=PhysicalState.LIQUID,
    )
    molar_mass = models.DecimalField(
        "Massa molar (g/mol)",
        max_digits=8, decimal_places=3,
        null=True, blank=True,
    )
    ph_value = models.DecimalField(
        "pH (aprox.)",
        max_digits=4, decimal_places=2,
        null=True, blank=True,
        help_text="Quando aplicável a soluções aquosas.",
    )

    # ─── Reactivity flags (used by the rules engine) ───────────────────────
    # NOTE: these flags drive deterministic rules in compatibility/rules.py.
    # Keep field names stable — the engine references them by name.
    is_acid = models.BooleanField("É ácido", default=False)
    is_base = models.BooleanField("É base", default=False)
    is_water = models.BooleanField("É água", default=False)
    is_organic_solvent = models.BooleanField("Solvente orgânico", default=False)

    # ─── Safety & handling ─────────────────────────────────────────────────
    hazards = models.ManyToManyField(
        Hazard,
        related_name="substances",
        blank=True,
        verbose_name="Riscos",
    )
    required_ppe = models.JSONField(
        "EPIs recomendados",
        default=list,
        blank=True,
        help_text='Lista de EPIs (ex: ["luvas nitrílicas", "óculos de proteção"]).',
    )
    handling_notes = models.TextField(
        "Cuidados ao manipular",
        blank=True,
    )
    critical_alerts = models.TextField(
        "Alertas críticos",
        blank=True,
        help_text="Avisos de segurança que devem aparecer em destaque.",
    )

    # ─── Storage ───────────────────────────────────────────────────────────
    storage_instructions = models.TextField(
        "Instruções de armazenamento",
        blank=True,
    )
    storage_incompatibilities = models.TextField(
        "Incompatibilidades de armazenamento",
        blank=True,
        help_text="Substâncias / classes que não podem ser estocadas próximas.",
    )

    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Substância"
        verbose_name_plural = "Substâncias"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["cas_number"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    @property
    def hazard_codes(self) -> list[str]:
        """Return the canonical hazard codes attached to this substance."""
        return list(self.hazards.values_list("code", flat=True))
