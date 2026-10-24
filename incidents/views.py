
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.views.decorators.http import require_POST
from django.contrib import messages

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Incident
from .forms import IncidentForm
from .serializers import IncidentSerializer


@login_required
def dashboard(request):
    incidents = Incident.objects.all()

    search = request.GET.get("q", "").strip()
    severity = request.GET.get("severity", "")
    status = request.GET.get("status", "")

    if search:
        incidents = incidents.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(incident_type__icontains=search)
        )

    if severity in ["Critical", "High", "Medium", "Low"]:
        incidents = incidents.filter(severity=severity)

    if status in ["Open", "Investigating", "Resolved"]:
        incidents = incidents.filter(status=status)

    context = {
        "incidents": incidents,
        "total": Incident.objects.count(),
        "critical": Incident.objects.filter(
            severity="Critical"
        ).count(),
        "open_count": Incident.objects.filter(status="Open").count(),
        "resolved": Incident.objects.filter(status="Resolved").count(),
        "severity_data": list(
            Incident.objects.values("severity").annotate(
                count=Count("id")
            )
        ),
        "search": search,
        "selected_severity": severity,
        "selected_status": status,
    }
    return render(request, "incidents/dashboard.html", context)


@login_required
def incident_create(request):
    form = IncidentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Incident created successfully.")
        return redirect("dashboard")

    return render(
        request,
        "incidents/incident_form.html",
        {"form": form, "heading": "Create Incident"},
    )


@login_required
def incident_edit(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    form = IncidentForm(request.POST or None, instance=incident)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Incident updated successfully.")
        return redirect("dashboard")

    return render(
        request,
        "incidents/incident_form.html",
        {"form": form, "heading": "Edit Incident"},
    )


@login_required
@require_POST
def incident_delete(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    incident.delete()
    messages.success(request, "Incident deleted successfully.")
    return redirect("dashboard")


class IncidentViewSet(ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description", "incident_type", "source_ip"]
    ordering_fields = ["created_at", "severity", "status"]
