import json
import unittest

from src import alarm_to_incident
from src import create_incident
from src import escalate_incidents
from src import get_incident
from src import incident_store
from src import update_incident


def response_body(response):
    return json.loads(response["body"])


class Phase1HandlerTests(unittest.TestCase):
    def setUp(self):
        incident_store._clear_store()

    def test_create_valid_incident(self):
        event = {
            "body": json.dumps(
                {
                    "title": "High API latency",
                    "description": "The orders API is responding slowly.",
                    "severity": "high",
                    "service": "orders-api",
                }
            )
        }

        response = create_incident.handler(event, None)
        body = response_body(response)

        self.assertEqual(response["statusCode"], 201)
        self.assertEqual(body["title"], "High API latency")
        self.assertEqual(body["severity"], "HIGH")
        self.assertEqual(body["status"], "OPEN")
        self.assertIn("id", body)

    def test_reject_invalid_severity(self):
        event = {
            "body": json.dumps(
                {
                    "title": "Bad severity example",
                    "description": "This should fail validation.",
                    "severity": "urgent",
                    "service": "billing-api",
                }
            )
        }

        response = create_incident.handler(event, None)
        body = response_body(response)

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Invalid severity", body["error"])

    def test_get_existing_incident(self):
        incident = incident_store.create_incident(
            {
                "id": "incident-123",
                "title": "Existing incident",
                "description": "Created directly in the local store.",
                "severity": "MEDIUM",
                "service": "payments-api",
                "status": "OPEN",
                "createdAt": "2026-06-20T10:00:00Z",
                "updatedAt": "2026-06-20T10:00:00Z",
            }
        )

        response = get_incident.handler(
            {"pathParameters": {"incidentId": incident["id"]}},
            None,
        )
        body = response_body(response)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["id"], "incident-123")

    def test_get_missing_incident_returns_404(self):
        response = get_incident.handler(
            {"pathParameters": {"incidentId": "missing-incident"}},
            None,
        )
        body = response_body(response)

        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["error"], "Incident not found.")

    def test_update_status(self):
        incident_store.create_incident(
            {
                "id": "incident-456",
                "title": "Update me",
                "description": "Status should change.",
                "severity": "LOW",
                "service": "inventory-api",
                "status": "OPEN",
                "createdAt": "2026-06-20T10:00:00Z",
                "updatedAt": "2026-06-20T10:00:00Z",
            }
        )

        response = update_incident.handler(
            {
                "pathParameters": {"incidentId": "incident-456"},
                "body": json.dumps({"status": "investigating"}),
            },
            None,
        )
        body = response_body(response)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["status"], "INVESTIGATING")

    def test_alarm_to_incident_creates_deterministic_incident_id(self):
        event = {
            "time": "2026-06-20T14:25:30Z",
            "detail": {
                "alarmName": "checkout-api-high-5xx",
                "configuration": {
                    "description": "Checkout API 5xx error rate exceeded threshold."
                },
                "state": {
                    "value": "ALARM",
                    "reason": "Threshold crossed.",
                    "timestamp": "2026-06-20T14:25:30Z",
                },
            },
        }

        first = response_body(alarm_to_incident.handler(event, None))
        second = response_body(alarm_to_incident.handler(event, None))

        self.assertEqual(first["id"], second["id"])
        self.assertTrue(first["id"].startswith("alarm-"))

    def test_duplicate_alarm_event_does_not_create_duplicate_incidents(self):
        event = {
            "detail": {
                "alarmName": "billing-api-high-latency",
                "state": {
                    "value": "ALARM",
                    "reason": "Latency threshold crossed.",
                    "timestamp": "2026-06-20T15:00:00Z",
                },
            }
        }

        alarm_to_incident.handler(event, None)
        alarm_to_incident.handler(event, None)

        incidents = incident_store.list_incidents()
        self.assertEqual(len(incidents), 1)

    def test_escalation_changes_stale_open_incidents_to_escalated(self):
        incident_store.create_incident(
            {
                "id": "stale-open",
                "title": "Stale open incident",
                "description": "This incident should be escalated.",
                "severity": "HIGH",
                "service": "checkout-api",
                "status": "OPEN",
                "createdAt": "2026-06-20T10:00:00Z",
                "updatedAt": "2026-06-20T10:00:00Z",
            }
        )
        incident_store.create_incident(
            {
                "id": "new-open",
                "title": "New open incident",
                "description": "This incident is not stale.",
                "severity": "LOW",
                "service": "catalog-api",
                "status": "OPEN",
                "createdAt": "2026-06-20T12:00:00Z",
                "updatedAt": "2026-06-20T12:00:00Z",
            }
        )

        response = escalate_incidents.handler(
            {"beforeTimestamp": "2026-06-20T11:00:00Z"},
            None,
        )
        body = response_body(response)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["incidentIds"], ["stale-open"])
        self.assertEqual(incident_store.get_incident("stale-open")["status"], "ESCALATED")
        self.assertEqual(incident_store.get_incident("new-open")["status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
