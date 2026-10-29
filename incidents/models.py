from django.db import models
from django.contrib.auth.models import User


class Incident(models.Model):
    SEVERITY_CHOICES = [
        ("Critical", "Critical"),
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]

    STATUS_CHOICES = [
        ("Open", "Open"),
        ("Investigating", "Investigating"),
        ("Resolved", "Resolved"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    incident_type = models.CharField(max_length=100, default="Other")
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default="Medium",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Open",
    )
    source_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incidents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
