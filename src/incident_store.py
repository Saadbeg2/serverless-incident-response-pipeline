"""Small incident storage abstraction.

Phase 1 uses an in-memory dictionary so tests can run locally without AWS
credentials. A later phase will replace these internals with DynamoDB calls.
"""

from copy import deepcopy

_INCIDENTS = {}


def create_incident(item):
    """Create an incident, returning the existing item if the id already exists."""
    # TODO: Replace this in-memory write with DynamoDB PutItem.
    incident_id = item["id"]
    if incident_id not in _INCIDENTS:
        _INCIDENTS[incident_id] = deepcopy(item)
    return deepcopy(_INCIDENTS[incident_id])


def get_incident(incident_id):
    """Return one incident by id, or None when it does not exist."""
    # TODO: Replace this in-memory read with DynamoDB GetItem.
    item = _INCIDENTS.get(incident_id)
    return deepcopy(item) if item else None


def list_incidents(status=None, severity=None):
    """Return incidents filtered by optional status and severity."""
    # TODO: Replace this scan-style behavior with DynamoDB queries/indexes.
    incidents = list(_INCIDENTS.values())

    if status:
        incidents = [item for item in incidents if item.get("status") == status]
    if severity:
        incidents = [item for item in incidents if item.get("severity") == severity]

    return deepcopy(incidents)


def update_incident(incident_id, updates):
    """Update an existing incident and return it, or None when missing."""
    # TODO: Replace this in-memory update with DynamoDB UpdateItem.
    if incident_id not in _INCIDENTS:
        return None

    _INCIDENTS[incident_id].update(deepcopy(updates))
    return deepcopy(_INCIDENTS[incident_id])


def find_stale_open_incidents(before_timestamp):
    """Return OPEN incidents created before the provided timestamp."""
    # TODO: Replace this local filtering with a DynamoDB query or scan strategy.
    stale = [
        item
        for item in _INCIDENTS.values()
        if item.get("status") == "OPEN" and item.get("createdAt", "") < before_timestamp
    ]
    return deepcopy(stale)


def _clear_store():
    """Test helper for keeping unit tests isolated."""
    _INCIDENTS.clear()
