"""
FISPQ app — Models.

Models the 16-section Safety Data Sheet (FISPQ / SDS) structure per
ABNT NBR 14725. Focuses on sections that feed the compatibility engine:

  - Section 2: Hazard identification (GHS classification, H/P-phrases)
  - Section 7: Handling and storage (incompatibilities)
  - Section 9: Physical/chemical properties
  - Section 10: Stability and reactivity (incompatible materials)

Each FISPQ is linked 1:1 to a Substance. Data here is *source-of-truth*
for safety information — the Substance model's flags/hazards are derived
from FISPQ data via sync operations.
"""

from django.db import models
from substances.models import Substance


class FISPQ(models.Model):
    """
    A Safety Data Sheet record linked to a single substance.
    Stores structured data from the 16 official sections.
    """

    class DataSource(models.TextChoices):
        MANUAL = "manual", "Cadastro manual"
        PUBCHEM = "pubchem", "PubChem"
        ECHA = "echa", "ECHA (European Chemicals Agency)"
        MANUFACTURER = "manufacturer", "Fabricante"

    substance = models.OneToOneField(
        Substance,
        on_delete=models.CASCADE,
        related_name="fispq",
        verbose_name="Substância",
    )
    data_source = models.CharField(
        "Fonte dos dados",
        max_length=20,
        choices=DataSource.choices,
        default=DataSource.MANUAL,
    )
    source_url = models.URLField(
        "URL da fonte",
        blank=True,
        help_text="Link para o registro original (ex: PubChem CID page).",
    )
    revision_date = models.DateField(
        "Data de revisão",
        null=True, blank=True,
        help_text="Data da última revisão da FISPQ na fonte original.",
    )
    is_complete = models.BooleanField(
        "Dados completos",
        default=False,
        help_text="Indica se todas as seções relevantes foram preenchidas.",
    )

    # ─── Section 2: Hazard Identification ─────────────────────────────────
    ghs_classification = models.JSONField(
        "Classificação GHS",
        default=list,
        blank=True,
        help_text='Lista de classes de perigo GHS (ex: ["Flam. Liq. 2", "Acute Tox. 4"]).',
    )
    signal_word = models.CharField(
        "Palavra de sinalização",
        max_length=20,
        blank=True,
        help_text="'Perigo' ou 'Atenção' (Danger / Warning).",
    )
    h_phrases = models.JSONField(
        "Frases H (perigo)",
        default=list,
        blank=True,
        help_text='Ex: [{"code": "H225", "text": "Líquido e vapor altamente inflamáveis"}].',
    )
    p_phrases = models.JSONField(
        "Frases P (precaução)",
        default=list,
        blank=True,
        help_text='Ex: [{"code": "P210", "text": "Manter afastado de fontes de calor..."}].',
    )
    ghs_pictograms = models.JSONField(
        "Pictogramas GHS",
        default=list,
        blank=True,
        help_text='Códigos dos pictogramas (ex: ["GHS02", "GHS07"]).',
    )

    # ─── Section 5: Fire-fighting ─────────────────────────────────────────
    flash_point = models.DecimalField(
        "Ponto de fulgor (C)",
        max_digits=7, decimal_places=2,
        null=True, blank=True,
    )
    auto_ignition_temp = models.DecimalField(
        "Temperatura de autoignição (C)",
        max_digits=7, decimal_places=2,
        null=True, blank=True,
    )
    extinguishing_media = models.JSONField(
        "Meios de extinção",
        default=list,
        blank=True,
        help_text='Ex: ["CO2", "espuma", "pó químico"].',
    )

    # ─── Section 7: Handling and Storage ──────────────────────────────────
    handling_precautions = models.TextField(
        "Precauções de manuseio",
        blank=True,
    )
    storage_conditions = models.TextField(
        "Condições de armazenamento",
        blank=True,
    )
    incompatible_materials = models.JSONField(
        "Materiais incompatíveis (Seção 7)",
        default=list,
        blank=True,
        help_text='Lista de materiais/classes incompatíveis para armazenamento.',
    )

    # ─── Section 8: Exposure Controls / PPE ───────────────────────────────
    oel_ppm = models.DecimalField(
        "Limite de exposição (ppm)",
        max_digits=10, decimal_places=3,
        null=True, blank=True,
        help_text="OEL / TWA em ppm (quando aplicável).",
    )
    oel_mg_m3 = models.DecimalField(
        "Limite de exposição (mg/m3)",
        max_digits=10, decimal_places=3,
        null=True, blank=True,
    )
    recommended_ppe = models.JSONField(
        "EPIs recomendados (FISPQ)",
        default=list,
        blank=True,
    )

    # ─── Section 9: Physical/Chemical Properties ──────────────────────────
    boiling_point = models.DecimalField(
        "Ponto de ebulição (C)",
        max_digits=7, decimal_places=2,
        null=True, blank=True,
    )
    melting_point = models.DecimalField(
        "Ponto de fusão (C)",
        max_digits=7, decimal_places=2,
        null=True, blank=True,
    )
    density = models.DecimalField(
        "Densidade (g/cm3)",
        max_digits=7, decimal_places=4,
        null=True, blank=True,
    )
    vapor_pressure = models.DecimalField(
        "Pressão de vapor (mmHg a 25C)",
        max_digits=10, decimal_places=3,
        null=True, blank=True,
    )
    solubility_water = models.CharField(
        "Solubilidade em água",
        max_length=120,
        blank=True,
        help_text="Ex: 'miscível', 'insolúvel', '35 g/L a 20C'.",
    )
    log_p = models.DecimalField(
        "LogP (coef. partição octanol/água)",
        max_digits=6, decimal_places=3,
        null=True, blank=True,
    )

    # ─── Section 10: Stability and Reactivity ─────────────────────────────
    stability_notes = models.TextField(
        "Estabilidade",
        blank=True,
        help_text="Condições normais de estabilidade.",
    )
    conditions_to_avoid = models.JSONField(
        "Condições a evitar",
        default=list,
        blank=True,
        help_text='Ex: ["calor", "faíscas", "umidade"].',
    )
    incompatible_chemicals = models.JSONField(
        "Substâncias incompatíveis (Seção 10)",
        default=list,
        blank=True,
        help_text='Substâncias/classes com reação perigosa (ex: ["oxidantes fortes", "ácidos"]).',
    )
    hazardous_decomposition = models.JSONField(
        "Produtos de decomposição perigosos",
        default=list,
        blank=True,
        help_text='Ex: ["CO", "CO2", "vapores tóxicos"].',
    )

    # ─── Section 11: Toxicological Information ────────────────────────────
    ld50_oral = models.CharField(
        "DL50 oral",
        max_length=80,
        blank=True,
        help_text="Ex: '7060 mg/kg (rato)'.",
    )
    lc50_inhalation = models.CharField(
        "CL50 inalação",
        max_length=80,
        blank=True,
    )

    # ─── Metadata ─────────────────────────────────────────────────────────
    pubchem_cid = models.PositiveIntegerField(
        "PubChem CID",
        null=True, blank=True,
        unique=True,
        help_text="Compound ID no PubChem (para rastreabilidade).",
    )
    raw_data = models.JSONField(
        "Dados brutos da fonte",
        default=dict,
        blank=True,
        help_text="JSON completo retornado pela API (auditoria).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FISPQ"
        verbose_name_plural = "FISPQs"
        ordering = ["substance__name"]

    def __str__(self):
        return f"FISPQ: {self.substance.name}"

    @property
    def is_high_risk(self) -> bool:
        """Quick check if this substance has any high-severity GHS class."""
        danger_keywords = ["Acute Tox. 1", "Acute Tox. 2", "Flam. Liq. 1", "Expl."]
        return any(
            any(kw in cls for kw in danger_keywords)
            for cls in self.ghs_classification
        )
