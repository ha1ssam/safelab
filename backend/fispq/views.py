from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import FISPQ
from .serializers import (
    FISPQListSerializer,
    FISPQDetailSerializer,
    FISPQSafetyCardSerializer,
)


class FISPQViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for consulting FISPQ data.
    Read-only — data is populated via management commands.
    """

    queryset = FISPQ.objects.select_related("substance").all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["data_source", "is_complete", "signal_word"]
    search_fields = [
        "substance__name",
        "substance__cas_number",
        "substance__formula",
    ]

    def get_serializer_class(self):
        if self.action == "list":
            return FISPQListSerializer
        if self.action == "safety_card":
            return FISPQSafetyCardSerializer
        return FISPQDetailSerializer

    @action(detail=True, methods=["get"], url_path="safety-card")
    def safety_card(self, request, pk=None):
        """Returns a simplified safety card for quick consultation."""
        instance = self.get_object()
        serializer = FISPQSafetyCardSerializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-cas/(?P<cas>[\\d-]+)")
    def by_cas(self, request, cas=None):
        """Look up FISPQ by CAS number."""
        try:
            fispq = FISPQ.objects.select_related("substance").get(
                substance__cas_number=cas
            )
        except FISPQ.DoesNotExist:
            return Response(
                {"detail": f"FISPQ não encontrada para CAS {cas}."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = FISPQDetailSerializer(fispq)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """Returns statistics about the FISPQ database coverage."""
        from substances.models import Substance

        total_substances = Substance.objects.filter(is_active=True).count()
        total_fispq = FISPQ.objects.count()
        complete_fispq = FISPQ.objects.filter(is_complete=True).count()

        return Response({
            "total_substances": total_substances,
            "total_fispq": total_fispq,
            "complete_fispq": complete_fispq,
            "coverage_percent": round(
                (total_fispq / total_substances * 100) if total_substances else 0, 1
            ),
            "completeness_percent": round(
                (complete_fispq / total_fispq * 100) if total_fispq else 0, 1
            ),
            "by_source": dict(
                FISPQ.objects.values("data_source")
                .annotate(count=Count("id"))
                .values_list("data_source", "count")
            ),
        })
