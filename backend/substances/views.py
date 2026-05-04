"""
Substances app — Views.
CRUD for the substance catalog. Read access for any authenticated user;
write access restricted to supervisors.
"""

import unicodedata

from django.db.models import Q
from rest_framework import generics, permissions, filters
from drf_spectacular.utils import extend_schema_view, extend_schema
from django_filters.rest_framework import DjangoFilterBackend

from .models import Substance
from .serializers import SubstanceSerializer, SubstanceListSerializer


def _strip_accents(text: str) -> str:
    """Remove diacritics so 'agua' matches 'água', 'acido' matches 'Ácido'."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


class AccentInsensitiveSearchFilter(filters.SearchFilter):
    """
    Substring search that's case- AND accent-insensitive, and tokenized.

    Why we don't use DRF's stock SearchFilter:
      - it does icontains on the raw query, so "acido sulfurico" never
        matches "Ácido sulfúrico" (different bytes on SQLite, which has
        no unaccent extension by default).
      - it doesn't split a multi-word query into AND-joined tokens, so
        "acido cloridrico" doesn't combine "ácido" + "clorídrico" hits.

    Strategy: split the query into tokens, strip accents from both query
    and DB values, and require every token to appear somewhere in the
    name/formula/CAS haystack. Catalog is small (~300 rows) so we do the
    accent-insensitive pass in Python — simple and predictable.
    """

    def filter_queryset(self, request, queryset, view):
        raw = (request.query_params.get(self.search_param) or "").strip()
        if not raw:
            return queryset

        search_fields = getattr(view, "search_fields", None)
        if not search_fields:
            return queryset

        tokens = [_strip_accents(t).lower() for t in raw.split() if t]
        if not tokens:
            return queryset

        # SQLite icontains is byte-exact, so a DB-side prefilter would
        # discard "agua" before we ever get to compare against "água".
        # The catalog is small (~300 rows) — scanning in Python is fine,
        # and it lets a single AND of accent-insensitive tokens match
        # across name + formula + CAS in one pass.
        matching_ids = []
        for sub in queryset.only("id", "name", "formula", "cas_number"):
            haystack = _strip_accents(
                f"{sub.name} {sub.formula} {sub.cas_number}"
            ).lower()
            if all(tok in haystack for tok in tokens):
                matching_ids.append(sub.id)

        return queryset.filter(id__in=matching_ids)


class IsSupervisorOrReadOnly(permissions.BasePermission):
    """Read for any authenticated user; write only for supervisors/superusers."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_supervisor", False)
        )


@extend_schema_view(
    get=extend_schema(tags=["Substâncias"]),
    post=extend_schema(tags=["Substâncias"]),
)
class SubstanceListCreateView(generics.ListCreateAPIView):
    """List and create substances. Supports search by name/CAS/formula."""

    permission_classes = [IsSupervisorOrReadOnly]
    filter_backends = [DjangoFilterBackend, AccentInsensitiveSearchFilter, filters.OrderingFilter]
    search_fields = ("name", "formula", "cas_number")
    filterset_fields = ("physical_state", "is_active")
    ordering_fields = ("name", "created_at")
    ordering = ("name",)

    def get_queryset(self):
        qs = Substance.objects.prefetch_related("hazards").all()
        # Default to only active for non-supervisors
        if not getattr(self.request.user, "is_supervisor", False):
            qs = qs.filter(is_active=True)
        return qs

    def get_serializer_class(self):
        # Compact format for listing, full format for creating.
        if self.request.method == "GET":
            return SubstanceListSerializer
        return SubstanceSerializer


@extend_schema_view(
    get=extend_schema(tags=["Substâncias"]),
    put=extend_schema(tags=["Substâncias"]),
    patch=extend_schema(tags=["Substâncias"]),
    delete=extend_schema(tags=["Substâncias"]),
)
class SubstanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve / update / delete a substance (full payload)."""

    queryset = Substance.objects.prefetch_related("hazards").all()
    serializer_class = SubstanceSerializer
    permission_classes = [IsSupervisorOrReadOnly]
