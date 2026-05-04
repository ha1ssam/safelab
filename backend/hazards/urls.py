"""Hazards app — URL configuration."""

from django.urls import path
from .views import HazardListCreateView, HazardDetailView

app_name = "hazards"

urlpatterns = [
    path("", HazardListCreateView.as_view(), name="hazard-list"),
    path("<int:pk>/", HazardDetailView.as_view(), name="hazard-detail"),
]
