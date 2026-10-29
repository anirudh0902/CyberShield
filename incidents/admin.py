from django.contrib import admin
from .models import Incident


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "incident_type",
        "severity",
        "status",
        "assigned_to",
        "created_at",
    )
    list_filter = ("severity", "status", "incident_type", "assigned_to")
    search_fields = ("title", "description", "source_ip")
    readonly_fields = ("created_at", "updated_at")
