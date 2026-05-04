"""Compatibility app — Serializers."""

from rest_framework import serializers

from .models import CompatibilityRecord


class CompatibilityRecordSerializer(serializers.ModelSerializer):
    substance_a_name = serializers.CharField(source="substance_a.name", read_only=True)
    substance_b_name = serializers.CharField(source="substance_b.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    risk_level_display = serializers.CharField(source="get_risk_level_display", read_only=True)

    class Meta:
        model = CompatibilityRecord
        fields = (
            "id",
            "substance_a", "substance_a_name",
            "substance_b", "substance_b_name",
            "status", "status_display",
            "risk_level", "risk_level_display",
            "reaction_type", "notes",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "substance_a_name", "substance_b_name", "status_display", "risk_level_display")

    def validate(self, attrs):
        a = attrs.get("substance_a") or getattr(self.instance, "substance_a", None)
        b = attrs.get("substance_b") or getattr(self.instance, "substance_b", None)
        if a and b and a.id == b.id:
            raise serializers.ValidationError("Substâncias devem ser diferentes.")
        return attrs


class CompatibilityCheckRequestSerializer(serializers.Serializer):
    """Input payload for the /check endpoint."""

    substance_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=2,
        max_length=10,
        help_text="IDs das substâncias a comparar (mínimo 2, máximo 10).",
    )
