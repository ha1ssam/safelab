"""Substances app — Serializers."""

from rest_framework import serializers

from .models import Substance
from hazards.models import Hazard
from hazards.serializers import HazardSerializer


class SubstanceSerializer(serializers.ModelSerializer):
    """Full read serializer with nested hazard details."""

    hazards = HazardSerializer(many=True, read_only=True)
    hazard_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Hazard.objects.all(),
        write_only=True,
        required=False,
        source="hazards",
    )
    physical_state_display = serializers.CharField(
        source="get_physical_state_display", read_only=True
    )

    class Meta:
        model = Substance
        fields = (
            "id", "name", "formula", "cas_number", "description",
            "physical_state", "physical_state_display",
            "molar_mass", "ph_value",
            "is_acid", "is_base", "is_water", "is_organic_solvent",
            "hazards", "hazard_ids",
            "required_ppe", "handling_notes", "critical_alerts",
            "storage_instructions", "storage_incompatibilities",
            "is_active", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "physical_state_display")


class SubstanceListSerializer(serializers.ModelSerializer):
    """Compact serializer for list views and pickers."""

    hazard_codes = serializers.SerializerMethodField()
    physical_state_display = serializers.CharField(
        source="get_physical_state_display", read_only=True
    )

    class Meta:
        model = Substance
        fields = (
            "id", "name", "formula", "cas_number",
            "physical_state", "physical_state_display",
            "hazard_codes", "is_active",
        )

    def get_hazard_codes(self, obj):
        return obj.hazard_codes
