from rest_framework import serializers
from .models import FISPQ


class FISPQListSerializer(serializers.ModelSerializer):
    substance_name = serializers.CharField(source="substance.name", read_only=True)
    substance_id = serializers.IntegerField(source="substance.id", read_only=True)

    class Meta:
        model = FISPQ
        fields = [
            "id",
            "substance_id",
            "substance_name",
            "data_source",
            "signal_word",
            "ghs_pictograms",
            "is_complete",
            "updated_at",
        ]


class FISPQDetailSerializer(serializers.ModelSerializer):
    substance_name = serializers.CharField(source="substance.name", read_only=True)
    substance_id = serializers.IntegerField(source="substance.id", read_only=True)
    cas_number = serializers.CharField(source="substance.cas_number", read_only=True)
    formula = serializers.CharField(source="substance.formula", read_only=True)

    class Meta:
        model = FISPQ
        fields = [
            "id",
            "substance_id",
            "substance_name",
            "cas_number",
            "formula",
            "data_source",
            "source_url",
            "revision_date",
            "is_complete",
            # Section 2
            "ghs_classification",
            "signal_word",
            "h_phrases",
            "p_phrases",
            "ghs_pictograms",
            # Section 5
            "flash_point",
            "auto_ignition_temp",
            "extinguishing_media",
            # Section 7
            "handling_precautions",
            "storage_conditions",
            "incompatible_materials",
            # Section 8
            "oel_ppm",
            "oel_mg_m3",
            "recommended_ppe",
            # Section 9
            "boiling_point",
            "melting_point",
            "density",
            "vapor_pressure",
            "solubility_water",
            "log_p",
            # Section 10
            "stability_notes",
            "conditions_to_avoid",
            "incompatible_chemicals",
            "hazardous_decomposition",
            # Section 11
            "ld50_oral",
            "lc50_inhalation",
            # Meta
            "pubchem_cid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class FISPQSafetyCardSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for quick safety consultation.
    Shows only the critical safety information needed during handling.
    """
    substance_name = serializers.CharField(source="substance.name", read_only=True)
    hazards = serializers.SerializerMethodField()
    ppe = serializers.JSONField(source="substance.required_ppe", read_only=True)
    critical_alerts = serializers.CharField(source="substance.critical_alerts", read_only=True)

    class Meta:
        model = FISPQ
        fields = [
            "substance_name",
            "signal_word",
            "ghs_pictograms",
            "h_phrases",
            "hazards",
            "ppe",
            "critical_alerts",
            "incompatible_chemicals",
            "conditions_to_avoid",
            "flash_point",
        ]

    def get_hazards(self, obj) -> list[str]:
        return list(obj.substance.hazards.values_list("name", flat=True))
