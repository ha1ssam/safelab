"""Substances app — URL configuration."""

from django.urls import path
from .views import SubstanceListCreateView, SubstanceDetailView

app_name = "substances"

urlpatterns = [
    path("", SubstanceListCreateView.as_view(), name="substance-list"),
    path("<int:pk>/", SubstanceDetailView.as_view(), name="substance-detail"),
]
