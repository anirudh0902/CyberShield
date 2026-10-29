from django import forms
from .models import Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            "title",
            "description",
            "incident_type",
            "severity",
            "status",
            "assigned_to",
            "source_ip",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "e.g. Suspicious Login Attempt"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Incident details..."}
            ),
            "incident_type": forms.TextInput(
                attrs={"placeholder": "e.g. Phishing, Malware, Brute Force"}
            ),
            "source_ip": forms.TextInput(
                attrs={"placeholder": "e.g. 192.168.1.100"}
            ),
        }
