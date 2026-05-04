"""Hazards app — Admin configuration."""

from django.contrib import admin
from .models import Hazard


@admin.register(Hazard)
class HazardAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "default_severity", "pictogram")
    list_filter = ("default_severity",)
    search_fields = ("code", "name", "description")
