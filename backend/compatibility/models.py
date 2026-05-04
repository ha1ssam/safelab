"""
Compatibility app — Models.
Stores explicit, curated compatibility records between two substances.
The compatibility check first looks up these records, then falls back to the
deterministic rules engine, and finally to "unknown" if nothing applies.
"""

from django.db import models
from django.core.exceptions import ValidationError

from substances.models import Substance


class CompatibilityRecord(models.Model):
    """
    A curated, explicit compatibility entry between two substances.
    Always stored normalized so substance_a.id < substance_b.id (avoids duplicates).
    """

    class Status(models.TextChoices):
        SAFE = "safe", "Seguro"
        UNSAFE = "unsafe", "Não seguro"
        UNKNOWN = "unknown", "Desconhecido"

    class RiskLevel(models.TextChoices):
        LOW = "low", "Baixo"
        MEDIUM = "medium", "Médio"
        HIGH = "high", "Alto"

    substance_a = models.ForeignKey(
        Substance,
        on_delete=models.CASCADE,
        related_name="compatibility_records_as_a",
        verbose_name="Substância A",
    )
    substance_b = models.ForeignKey(
        Substance,
        on_delete=models.CASCADE,
        related_name="compatibility_records_as_b",
        verbose_name="Substância B",
    )
    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.UNKNOWN,
    )
    risk_level = models.CharField(
        "Nível de risco",
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
    )
    reaction_type = models.CharField(
        "Tipo de reação",
        max_length=120,
        blank=True,
        help_text="Ex: 'Reação exotérmica', 'Liberação de gás tóxico'.",
    )
    notes = models.TextField(
        "Observações",
        blank=True,
        help_text="Detalhes técnicos, referências e cuidados específicos.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registro de compatibilidade"
        verbose_name_plural = "Registros de compatibilidade"
        unique_together = ("substance_a", "substance_b")
        ordering = ["substance_a__name", "substance_b__name"]
        constraints = [
            # Django 5.1+ uses `condition`; older versions used `check`.
            models.CheckConstraint(
                condition=models.Q(substance_a__lt=models.F("substance_b")),
                name="compat_pair_normalized",
            ),
        ]

    def clean(self):
        if self.substance_a_id and self.substance_b_id and self.substance_a_id == self.substance_b_id:
            raise ValidationError("Não é possível registrar compatibilidade de uma substância com ela mesma.")

    def save(self, *args, **kwargs):
        # Always normalize so the pair (A, B) stores A.id < B.id.
        # This guarantees a single canonical row per pair regardless of input order.
        if (
            self.substance_a_id and self.substance_b_id
            and self.substance_a_id > self.substance_b_id
        ):
            self.substance_a_id, self.substance_b_id = self.substance_b_id, self.substance_a_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.substance_a} ↔ {self.substance_b} ({self.get_status_display()})"
