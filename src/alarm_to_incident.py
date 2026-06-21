"""Lambda handler for converting CloudWatch alarm events into incidents."""

import hashlib

from src.incident_store import create_incident
from src.models import utc_now
from src.response import success_response


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

    # Idempotency matters because CloudWatch alarms can repeat, retry delivery,
    # or flap between states. A deterministic id lets repeated delivery of the
    # same alarm state change return the existing incident instead of creating
    # duplicate work for engineers.
    incident_id = _deterministic_alarm_incident_id(alarm_name, state_change_timestamp)
    now = utc_now()

    incident = {
        "id": incident_id,
        "title": f"CloudWatch alarm: {alarm_name}",
        "description": description,
        "severity": "HIGH",
        "service": alarm_name,
        "status": "OPEN",
        "source": "cloudwatch",
        "alarmName": alarm_name,
        "alarmState": state_value,
        "alarmTimestamp": state_change_timestamp,
        "createdAt": now,
        "updatedAt": now,
    }

    return success_response(create_incident(incident), status_code=201)
