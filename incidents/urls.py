
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    dashboard,
    incident_create,
    incident_edit,
    incident_delete,
    IncidentViewSet,
)

router = DefaultRouter()
router.register("incidents", IncidentViewSet, basename="incident")

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("incidents/create/", incident_create, name="incident_create"),
    path("incidents/<int:pk>/edit/", incident_edit, name="incident_edit"),
    path("incidents/<int:pk>/delete/", incident_delete, name="incident_delete"),
    path("api/", include(router.urls)),
]
