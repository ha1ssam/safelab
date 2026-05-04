"""Substances app — Admin configuration."""

from django.contrib import admin
from .models import Substance


@admin.register(Substance)
class SubstanceAdmin(admin.ModelAdmin):
    list_display = ("name", "formula", "cas_number", "physical_state", "is_active")
    list_filter = ("physical_state", "is_active", "is_acid", "is_base", "is_water", "is_organic_solvent", "hazards")
    search_fields = ("name", "formula", "cas_number", "description")
    filter_horizontal = ("hazards",)
    fieldsets = (
        ("Identificação", {
            "fields": ("name", "formula", "cas_number", "description"),
        }),
        ("Propriedades físicas", {
            "fields": ("physical_state", "molar_mass", "ph_value"),
        }),
        ("Propriedades reativas (motor de regras)", {
            "fields": ("is_acid", "is_base", "is_water", "is_organic_solvent"),
        }),
        ("Riscos & Manuseio", {
            "fields": ("hazards", "required_ppe", "handling_notes", "critical_alerts"),
        }),
        ("Armazenamento", {
            "fields": ("storage_instructions", "storage_incompatibilities"),
        }),
        ("Status", {"fields": ("is_active",)}),
    )
