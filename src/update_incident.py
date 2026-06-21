"""Lambda handler for updating incidents through the API."""

import json

try:
    from .incident_store import update_incident
    from .models import normalize_choice, utc_now, validate_incident_input
    from .response import error_response, success_response
except ImportError:
    from incident_store import update_incident
    from models import normalize_choice, utc_now, validate_incident_input
    from response import error_response, success_response

ALLOWED_UPDATE_FIELDS = {"status", "severity", "description", "service"}


def _parse_body(event):
    body = event.get("body") or {}
    if isinstance(body, str):
        return json.loads(body)
    return body

def handler(event, context):
    """Update allowed fields on an existing incident."""
    path = event.get("pathParameters") or {}
    incident_id = path.get("incidentId")
    if not incident_id:
        return error_response("Missing path parameter: incidentId.")

    try:
        body = _parse_body(event)
    except json.JSONDecodeError:
        return error_response("Request body must be valid JSON.")

    errors = validate_incident_input(body)
    if errors:
        return error_response(" ".join(errors))

    updates = {key: body[key] for key in ALLOWED_UPDATE_FIELDS if key in body}
    if not updates:
        return error_response("No supported update fields provided.")

    if "status" in updates:
        updates["status"] = normalize_choice(updates["status"])
    if "severity" in updates:
        updates["severity"] = normalize_choice(updates["severity"])
    updates["updatedAt"] = utc_now()

    incident = update_incident(incident_id, updates)
    if not incident:
        return error_response("Incident not found.", status_code=404)

    return success_response(incident)
