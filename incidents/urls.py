from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    dashboard,
    incident_create,
    incident_edit,
    incident_delete,
    incident_resolve,
    incident_status_update,
    threat_detection_view,
    export_incidents_csv,
    IncidentViewSet,
)

router = DefaultRouter()
router.register("incidents", IncidentViewSet, basename="incident")

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("incidents/create/", incident_create, name="incident_create"),
    path("incidents/<int:pk>/edit/", incident_edit, name="incident_edit"),
    path("incidents/<int:pk>/resolve/", incident_resolve, name="incident_resolve"),
    path("incidents/<int:pk>/status/", incident_status_update, name="incident_status_update"),
    path("incidents/<int:pk>/delete/", incident_delete, name="incident_delete"),
    path("incidents/export/csv/", export_incidents_csv, name="incident_export_csv"),
    path("threat-detection/", threat_detection_view, name="threat_detection"),
    path("api/", include(router.urls)),
]
