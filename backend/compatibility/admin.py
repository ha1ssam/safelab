"""Compatibility app — Admin configuration."""

from django.contrib import admin
from .models import CompatibilityRecord


@admin.register(CompatibilityRecord)
class CompatibilityRecordAdmin(admin.ModelAdmin):
    list_display = ("substance_a", "substance_b", "status", "risk_level", "reaction_type")
    list_filter = ("status", "risk_level")
    search_fields = ("substance_a__name", "substance_b__name", "reaction_type", "notes")
    autocomplete_fields = ("substance_a", "substance_b")
