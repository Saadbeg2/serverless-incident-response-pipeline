"""Lambda handler for reading a single incident through the API."""

try:
    from .incident_store import get_incident
    from .response import error_response, success_response
except ImportError:
    from incident_store import get_incident
    from response import error_response, success_response

def handler(event, context):
    """Get an incident by id from API Gateway path parameters."""
    path = event.get("pathParameters") or {}
    incident_id = path.get("incidentId")
    if not incident_id:
        return error_response("Missing path parameter: incidentId.")

    incident = get_incident(incident_id)
    if not incident:
        return error_response("Incident not found.", status_code=404)

    return success_response(incident)
