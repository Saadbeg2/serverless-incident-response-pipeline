"""Small incident storage abstraction.

Local tests use an in-memory dictionary when INCIDENTS_TABLE_NAME is not set.
Deployed Lambdas use DynamoDB when INCIDENTS_TABLE_NAME is available.
"""

from copy import deepcopy
import os

_INCIDENTS = {}
_TABLE = None


def _table_name():
    return os.environ.get("INCIDENTS_TABLE_NAME")


def _use_dynamodb():
    return bool(_table_name())


def _dynamodb_table():
    """Load the DynamoDB table lazily so local tests do not need boto3."""
    global _TABLE
    if _TABLE is None:
        import boto3

        _TABLE = boto3.resource("dynamodb").Table(_table_name())
    return _TABLE


def create_incident(item):
    """Create an incident, returning the existing item if the id already exists."""
    if _use_dynamodb():
        table = _dynamodb_table()
        try:
            table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(id)",
            )
            return deepcopy(item)
        except table.meta.client.exceptions.ConditionalCheckFailedException:
            return get_incident(item["id"])

    incident_id = item["id"]
    if incident_id not in _INCIDENTS:
        _INCIDENTS[incident_id] = deepcopy(item)
    return deepcopy(_INCIDENTS[incident_id])


def get_incident(incident_id):
    """Return one incident by id, or None when it does not exist."""
    if _use_dynamodb():
        response = _dynamodb_table().get_item(Key={"id": incident_id})
        return response.get("Item")

    item = _INCIDENTS.get(incident_id)
    return deepcopy(item) if item else None


def list_incidents(status=None, severity=None):
    """Return incidents filtered by optional status and severity."""
    if _use_dynamodb():
        # Phase 2 keeps the table simple with only a primary key. Later phases
        # can add indexes when access patterns are proven.
        incidents = []
        scan_kwargs = {}
        table = _dynamodb_table()

        while True:
            response = table.scan(**scan_kwargs)
            incidents.extend(response.get("Items", []))
            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break
            scan_kwargs["ExclusiveStartKey"] = last_key

        if status:
            incidents = [item for item in incidents if item.get("status") == status]
        if severity:
            incidents = [item for item in incidents if item.get("severity") == severity]
        return incidents

    incidents = list(_INCIDENTS.values())

    if status:
        incidents = [item for item in incidents if item.get("status") == status]
    if severity:
        incidents = [item for item in incidents if item.get("severity") == severity]

    return deepcopy(incidents)


def update_incident(incident_id, updates):
    """Update an existing incident and return it, or None when missing."""
    if _use_dynamodb():
        if not updates:
            return get_incident(incident_id)

        names = {}
        values = {}
        assignments = []
        for index, (key, value) in enumerate(updates.items()):
            name_key = f"#field{index}"
            value_key = f":value{index}"
            names[name_key] = key
            values[value_key] = value
            assignments.append(f"{name_key} = {value_key}")

        try:
            response = _dynamodb_table().update_item(
                Key={"id": incident_id},
                UpdateExpression="SET " + ", ".join(assignments),
                ConditionExpression="attribute_exists(id)",
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
                ReturnValues="ALL_NEW",
            )
            return response.get("Attributes")
        except _dynamodb_table().meta.client.exceptions.ConditionalCheckFailedException:
            return None

    if incident_id not in _INCIDENTS:
        return None

    _INCIDENTS[incident_id].update(deepcopy(updates))
    return deepcopy(_INCIDENTS[incident_id])


def find_stale_open_incidents(before_timestamp):
    """Return OPEN incidents created before the provided timestamp."""
    if _use_dynamodb():
        # This intentionally starts with a scan because Phase 2 has a small,
        # low-traffic table. A later phase can add a GSI for status/createdAt.
        return [
            item
            for item in list_incidents(status="OPEN")
            if item.get("createdAt", "") < before_timestamp
        ]

    stale = [
        item
        for item in _INCIDENTS.values()
        if item.get("status") == "OPEN" and item.get("createdAt", "") < before_timestamp
    ]
    return deepcopy(stale)


def _clear_store():
    """Test helper for keeping unit tests isolated."""
    _INCIDENTS.clear()
