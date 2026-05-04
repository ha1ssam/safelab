"""
Compatibility app — Views.

- `CompatibilityRecordListCreateView` / `CompatibilityRecordDetailView`:
   CRUD over the curated record catalog (supervisor-only writes).
- `check_compatibility_view`: stateless endpoint that runs the full pipeline
   (records + rules engine) and returns a consolidated verdict.
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes as perm_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import CompatibilityRecord
from .serializers import (
    CompatibilityRecordSerializer,
    CompatibilityCheckRequestSerializer,
)
from .services import check_compatibility


class IsSupervisorOrReadOnly(permissions.BasePermission):
    """Any authenticated user can read; only supervisors can write."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_supervisor", False)
        )


@extend_schema_view(
    get=extend_schema(tags=["Compatibilidade"]),
    post=extend_schema(tags=["Compatibilidade"]),
)
class CompatibilityRecordListCreateView(generics.ListCreateAPIView):
    queryset = CompatibilityRecord.objects.select_related("substance_a", "substance_b").all()
    serializer_class = CompatibilityRecordSerializer
    permission_classes = [IsSupervisorOrReadOnly]
    filterset_fields = ("status", "risk_level")
    search_fields = ("substance_a__name", "substance_b__name", "reaction_type")


@extend_schema_view(
    get=extend_schema(tags=["Compatibilidade"]),
    put=extend_schema(tags=["Compatibilidade"]),
    patch=extend_schema(tags=["Compatibilidade"]),
    delete=extend_schema(tags=["Compatibilidade"]),
)
class CompatibilityRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompatibilityRecord.objects.select_related("substance_a", "substance_b").all()
    serializer_class = CompatibilityRecordSerializer
    permission_classes = [IsSupervisorOrReadOnly]


@extend_schema(
    tags=["Compatibilidade"],
    request=CompatibilityCheckRequestSerializer,
    description=(
        "Executa o motor de compatibilidade. Para cada par de substâncias, retorna "
        "status (safe/unsafe/unknown), nível de risco (low/medium/high), tipo de reação "
        "e observações. Combina registros curados + motor de regras determinístico."
    ),
)
@api_view(["POST"])
@perm_classes([permissions.IsAuthenticated])
def check_compatibility_view(request):
    """Stateless endpoint: receives substance IDs, returns the full check report."""
    serializer = CompatibilityCheckRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        result = check_compatibility(serializer.validated_data["substance_ids"])
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(result.as_dict(), status=status.HTTP_200_OK)
