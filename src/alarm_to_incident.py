"""Lambda handler for converting CloudWatch alarm events into incidents."""

import hashlib

try:
    from .alerts import publish_incident_alert
    from .incident_store import create_incident, get_incident
    from .models import normalize_choice, utc_now
    from .response import success_response
except ImportError:
    from alerts import publish_incident_alert
    from incident_store import create_incident, get_incident
    from models import normalize_choice, utc_now
    from response import success_response


def _deterministic_alarm_incident_id(alarm_name, state_change_timestamp):
    key = f"{alarm_name}|{state_change_timestamp}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return f"alarm-{digest}"

def handler(event, context):
    """Create an incident from a CloudWatch alarm state-change event."""
    detail = event.get("detail", {})
    alarm_name = detail.get("alarmName", "unknown-alarm")
    state = detail.get("state", {})
    state_value = state.get("value", "UNKNOWN")
    state_reason = state.get("reason", "No alarm reason provided.")
    state_change_timestamp = state.get("timestamp") or event.get("time") or utc_now()
    configuration = detail.get("configuration", {})
    description = configuration.get("description") or state_reason
    severity = normalize_choice(detail.get("severity") or "HIGH")

    # Idempotency matters because CloudWatch alarms can repeat, retry delivery,
    # or flap between states. A deterministic id lets repeated delivery of the
    # same alarm state change return the existing incident instead of creating
    # duplicate work or duplicate alert emails for engineers.
    incident_id = _deterministic_alarm_incident_id(alarm_name, state_change_timestamp)
    existing_incident = get_incident(incident_id)
    if existing_incident:
        return success_response(existing_incident, status_code=200)

    now = utc_now()

    incident = {
        "id": incident_id,
        "title": f"CloudWatch alarm: {alarm_name}",
        "description": description,
        "severity": severity,
        "service": alarm_name,
        "status": "OPEN",
        "source": "cloudwatch",
        "alarmName": alarm_name,
        "alarmState": state_value,
        "alarmTimestamp": state_change_timestamp,
        "createdAt": now,
        "updatedAt": now,
    }

    created_incident = create_incident(incident)
    publish_incident_alert(created_incident)
    return success_response(created_incident, status_code=201)
