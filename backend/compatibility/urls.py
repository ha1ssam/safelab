"""Compatibility app — URL configuration."""

from django.urls import path
from .views import (
    CompatibilityRecordListCreateView,
    CompatibilityRecordDetailView,
    check_compatibility_view,
)

app_name = "compatibility"

urlpatterns = [
    path("records/", CompatibilityRecordListCreateView.as_view(), name="record-list"),
    path("records/<int:pk>/", CompatibilityRecordDetailView.as_view(), name="record-detail"),
    path("check/", check_compatibility_view, name="check"),
]
