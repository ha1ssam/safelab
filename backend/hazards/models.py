"""
Hazards app — Models.
Catalogs the canonical hazard categories (GHS-inspired) used across the system.
A Hazard is a *type* of risk; substances reference Hazards via a many-to-many relation
defined in the substances app.
"""

from django.db import models


class Hazard(models.Model):
    """
    A canonical hazard category (e.g. flammable, corrosive, toxic, oxidizer).

    The `code` is used as a stable identifier for the rules engine — the engine
    references hazards by code, never by name or PK, so codes must remain stable
    once seeded.
    """

    class Code(models.TextChoices):
        FLAMMABLE = "flammable", "Inflamável"
        CORROSIVE = "corrosive", "Corrosivo"
        TOXIC = "toxic", "Tóxico"
        OXIDIZER = "oxidizer", "Oxidante"
        REACTIVE_WATER = "reactive_water", "Reage com água"
        EXPLOSIVE = "explosive", "Explosivo"
        IRRITANT = "irritant", "Irritante"
        CARCINOGEN = "carcinogen", "Carcinogênico"
        ENV_HAZARD = "env_hazard", "Perigoso ao meio ambiente"
        COMPRESSED_GAS = "compressed_gas", "Gás comprimido"

    class Severity(models.TextChoices):
        LOW = "low", "Baixa"
        MEDIUM = "medium", "Média"
        HIGH = "high", "Alta"

    code = models.CharField(
        "Código",
        max_length=30,
        unique=True,
        choices=Code.choices,
        help_text="Identificador estável usado pelo motor de regras.",
    )
    name = models.CharField("Nome", max_length=80)
    description = models.TextField("Descrição", blank=True)
    default_severity = models.CharField(
        "Severidade padrão",
        max_length=10,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )
    pictogram = models.CharField(
        "Pictograma (ícone)",
        max_length=50,
        blank=True,
        help_text="Nome do ícone (lucide-react) usado no frontend.",
    )

    class Meta:
        verbose_name = "Risco"
        verbose_name_plural = "Riscos"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_default_severity_display()})"
