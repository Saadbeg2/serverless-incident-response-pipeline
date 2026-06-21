"""Shared incident validation and formatting helpers."""

from datetime import datetime, timezone

ALLOWED_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
ALLOWED_STATUSES = {"OPEN", "INVESTIGATING", "RESOLVED", "ESCALATED"}


def utc_now():
    """Return the current UTC time in an API-friendly ISO 8601 format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_choice(value):
    """Normalize severity and status values to uppercase strings."""
    if value is None:
        return None
    return str(value).strip().upper()


def validate_incident_input(data, required_fields=None):
    """Validate common incident fields and return a list of readable errors."""
    required_fields = required_fields or []
    errors = []

    if not isinstance(data, dict):
        return ["Request body must be a JSON object."]

    for field in required_fields:
        if not data.get(field):
            errors.append(f"Missing required field: {field}.")

    severity = data.get("severity")
    if severity is not None and normalize_choice(severity) not in ALLOWED_SEVERITIES:
        allowed = ", ".join(sorted(ALLOWED_SEVERITIES))
        errors.append(f"Invalid severity. Allowed values: {allowed}.")

    status = data.get("status")
    if status is not None and normalize_choice(status) not in ALLOWED_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_STATUSES))
        errors.append(f"Invalid status. Allowed values: {allowed}.")

    return errors
