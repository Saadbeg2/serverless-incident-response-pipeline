"""Lambda handler for creating incidents through the API."""

import json
from uuid import uuid4

from src.incident_store import create_incident
from src.models import normalize_choice, utc_now, validate_incident_input
from src.response import error_response, success_response

REQUIRED_FIELDS = ["title", "description", "severity", "service"]


def _parse_body(event):
    body = event.get("body") or {}
    if isinstance(body, str):
        return json.loads(body)
    return body

def handler(event, context):
    """Create an incident from an API Gateway-style event."""
    try:
        body = _parse_body(event)
    except json.JSONDecodeError:
        return error_response("Request body must be valid JSON.")

    errors = validate_incident_input(body, REQUIRED_FIELDS)
    if errors:
        return error_response(" ".join(errors))

    now = utc_now()
    incident = {
        "id": str(uuid4()),
        "title": body["title"],
        "description": body["description"],
        "severity": normalize_choice(body["severity"]),
        "service": body["service"],
        "status": "OPEN",
        "createdAt": now,
        "updatedAt": now,
    }

    return success_response(create_incident(incident), status_code=201)
