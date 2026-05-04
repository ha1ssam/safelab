from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FISPQViewSet

router = DefaultRouter()
router.register(r"fispq", FISPQViewSet, basename="fispq")

urlpatterns = [
    path("", include(router.urls)),
]
