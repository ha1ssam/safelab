"""Hazards app — Views."""

from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import Hazard
from .serializers import HazardSerializer


class IsSupervisorOrReadOnly(permissions.BasePermission):
    """Read for any authenticated user; write only for supervisors."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "is_supervisor", False))


@extend_schema_view(
    get=extend_schema(tags=["Riscos"]),
    post=extend_schema(tags=["Riscos"]),
)
class HazardListCreateView(generics.ListCreateAPIView):
    queryset = Hazard.objects.all()
    serializer_class = HazardSerializer
    permission_classes = [IsSupervisorOrReadOnly]
    search_fields = ("name", "code")


@extend_schema_view(
    get=extend_schema(tags=["Riscos"]),
    put=extend_schema(tags=["Riscos"]),
    patch=extend_schema(tags=["Riscos"]),
    delete=extend_schema(tags=["Riscos"]),
)
class HazardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hazard.objects.all()
    serializer_class = HazardSerializer
    permission_classes = [IsSupervisorOrReadOnly]
