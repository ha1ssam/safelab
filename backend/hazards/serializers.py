"""Hazards app — Serializers."""

from rest_framework import serializers
from .models import Hazard


class HazardSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source="get_default_severity_display", read_only=True)
    code_display = serializers.CharField(source="get_code_display", read_only=True)

    class Meta:
        model = Hazard
        fields = (
            "id", "code", "code_display", "name", "description",
            "default_severity", "severity_display", "pictogram",
        )
        read_only_fields = ("id", "severity_display", "code_display")
