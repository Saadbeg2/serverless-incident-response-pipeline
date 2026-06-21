"""Lambda handler for scheduled incident escalation checks."""

from src.incident_store import find_stale_open_incidents, update_incident
from src.models import utc_now
from src.response import error_response, success_response

def handler(event, context):
    """Escalate OPEN incidents older than a local-test cutoff timestamp."""
    before_timestamp = event.get("beforeTimestamp") or event.get("cutoffTimestamp")
    if not before_timestamp:
        return error_response("Missing cutoff timestamp. Use beforeTimestamp.")

    stale_incidents = find_stale_open_incidents(before_timestamp)
    escalated_ids = []
    now = utc_now()

    for incident in stale_incidents:
        updated = update_incident(
            incident["id"],
            {"status": "ESCALATED", "updatedAt": now},
        )
        if updated:
            escalated_ids.append(updated["id"])

    return success_response({"count": len(escalated_ids), "incidentIds": escalated_ids})
