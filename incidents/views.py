import csv
from django.http import HttpResponse
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
from .threat_detector import DETECTION_RULES, scan_activity


@login_required
def dashboard(request):
    incidents = Incident.objects.select_related("assigned_to").all()

    search = request.GET.get("q", "").strip()
    severity = request.GET.get("severity", "")
    status = request.GET.get("status", "")

    if search:
        incidents = incidents.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(incident_type__icontains=search)
            | Q(source_ip__icontains=search)
            | Q(assigned_to__username__icontains=search)
        )

    if severity in ["Critical", "High", "Medium", "Low"]:
        incidents = incidents.filter(severity=severity)

    if status in ["Open", "Investigating", "Resolved"]:
        incidents = incidents.filter(status=status)

    context = {
        "incidents": incidents,
        "total": Incident.objects.count(),
        "critical": Incident.objects.filter(severity="Critical").count(),
        "open_count": Incident.objects.filter(status="Open").count(),
        "resolved": Incident.objects.filter(status="Resolved").count(),
        "severity_data": list(
            Incident.objects.values("severity").annotate(count=Count("id"))
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
        incident = form.save(commit=False)
        # Rule check: if incident_type is Other/default, check if rules detect a known pattern
        if incident.incident_type in ["Other", "", None]:
            matches = scan_activity(f"{incident.title} {incident.description}")
            if matches:
                incident.incident_type = matches[0]["type"]
                incident.severity = matches[0]["severity"]
        incident.save()
        messages.success(request, f"Incident #{incident.id} created successfully.")
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
        messages.success(request, f"Incident #{incident.id} updated successfully.")
        return redirect("dashboard")

    return render(
        request,
        "incidents/incident_form.html",
        {"form": form, "heading": "Edit Incident"},
    )


@login_required
@require_POST
def incident_resolve(request, pk):
    """Quick 1-click resolve action."""
    incident = get_object_or_404(Incident, pk=pk)
    incident.status = "Resolved"
    incident.save(update_fields=["status", "updated_at"])
    messages.success(request, f"Incident #{incident.id} marked as Resolved.")
    return redirect("dashboard")


@login_required
@require_POST
def incident_status_update(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    new_status = request.POST.get("status")
    if new_status in dict(Incident.STATUS_CHOICES):
        incident.status = new_status
        incident.save(update_fields=["status", "updated_at"])
        messages.success(request, f"Incident #{incident.id} status updated to '{new_status}'.")
    return redirect("dashboard")


@login_required
def threat_detection_view(request):
    """Scan suspicious activity using rules and optionally convert to incident."""
    log_text = request.POST.get("log_text", "") or request.GET.get("log_text", "")
    source_ip = request.POST.get("source_ip", "").strip() or request.GET.get("source_ip", "").strip()
    matches = scan_activity(log_text) if log_text else []

    if request.method == "POST" and request.POST.get("action") == "create_incident" and matches:
        top_threat = matches[0]
        incident = Incident.objects.create(
            title=f"Detected: {top_threat['name']}",
            description=f"Rule Matched: {top_threat['name']} ({top_threat['rule_id']})\n"
                        f"Indicator: {top_threat['matched_text']}\n"
                        f"Description: {top_threat['description']}\n\n"
                        f"Activity Log:\n{log_text}",
            incident_type=top_threat["type"],
            severity=top_threat["severity"],
            status="Open",
            source_ip=source_ip or None,
            assigned_to=request.user,
        )
        messages.success(request, f"Incident #{incident.id} created from rule match and assigned to {request.user.username}.")
        return redirect("dashboard")

    return render(
        request,
        "incidents/threat_detection.html",
        {
            "rules": DETECTION_RULES,
            "log_text": log_text,
            "source_ip": source_ip,
            "matches": matches,
        },
    )


@login_required
def export_incidents_csv(request):
    """Export accurate incident dataset as downloadable CSV report."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="cyber_shield_incidents.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "Incident ID",
        "Title",
        "Incident Type",
        "Severity",
        "Status",
        "Assigned To",
        "Source IP",
        "Created At",
        "Updated At",
    ])
    for inc in Incident.objects.select_related("assigned_to").all():
        writer.writerow([
            inc.id,
            inc.title,
            inc.incident_type,
            inc.severity,
            inc.status,
            inc.assigned_to.username if inc.assigned_to else "Unassigned",
            inc.source_ip or "N/A",
            inc.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            inc.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])
    return response


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
