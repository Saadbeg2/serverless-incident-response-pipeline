"""Lambda handler for listing incidents through the API."""

from src.incident_store import list_incidents
from src.models import ALLOWED_SEVERITIES, ALLOWED_STATUSES, normalize_choice
from src.response import error_response, success_response

def handler(event, context):
    """List incidents with optional status and severity filters."""
    query = event.get("queryStringParameters") or {}
    status = normalize_choice(query.get("status"))
    severity = normalize_choice(query.get("severity"))

    if status and status not in ALLOWED_STATUSES:
        return error_response("Invalid status filter.")
    if severity and severity not in ALLOWED_SEVERITIES:
        return error_response("Invalid severity filter.")

    incidents = list_incidents(status=status, severity=severity)
    return success_response({"incidents": incidents, "count": len(incidents)})
