from django.contrib import admin
from .models import FISPQ


@admin.register(FISPQ)
class FISPQAdmin(admin.ModelAdmin):
    list_display = [
        "substance",
        "data_source",
        "signal_word",
        "is_complete",
        "pubchem_cid",
        "updated_at",
    ]
    list_filter = ["data_source", "is_complete", "signal_word"]
    search_fields = ["substance__name", "substance__cas_number"]
    readonly_fields = ["created_at", "updated_at", "raw_data"]

    fieldsets = (
        ("Substância", {
            "fields": ("substance", "data_source", "source_url", "revision_date", "is_complete"),
        }),
        ("Seção 2 — Identificação de Perigos", {
            "fields": (
                "ghs_classification", "signal_word",
                "h_phrases", "p_phrases", "ghs_pictograms",
            ),
        }),
        ("Seção 5 — Combate a Incêndio", {
            "fields": ("flash_point", "auto_ignition_temp", "extinguishing_media"),
        }),
        ("Seção 7 — Manuseio e Armazenamento", {
            "fields": ("handling_precautions", "storage_conditions", "incompatible_materials"),
        }),
        ("Seção 8 — Controle de Exposição / EPIs", {
            "fields": ("oel_ppm", "oel_mg_m3", "recommended_ppe"),
        }),
        ("Seção 9 — Propriedades Físico-Químicas", {
            "fields": (
                "boiling_point", "melting_point", "density",
                "vapor_pressure", "solubility_water", "log_p",
            ),
        }),
        ("Seção 10 — Estabilidade e Reatividade", {
            "fields": (
                "stability_notes", "conditions_to_avoid",
                "incompatible_chemicals", "hazardous_decomposition",
            ),
        }),
        ("Seção 11 — Toxicologia", {
            "fields": ("ld50_oral", "lc50_inhalation"),
        }),
        ("Metadados", {
            "fields": ("pubchem_cid", "raw_data", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
