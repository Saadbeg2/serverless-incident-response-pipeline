"""Optional SNS alert publishing helpers."""

import os

ALERTABLE_SEVERITIES = {"HIGH", "CRITICAL"}


def _sns_client():
    """Load boto3 lazily so local tests do not need AWS credentials."""
    import boto3

    return boto3.client("sns")


def publish_incident_alert(incident):
    """Publish an SNS alert for high-severity incidents when configured.

    SNS alerting is controlled by INCIDENT_ALERT_TOPIC_ARN. If the variable is
    missing, local tests and non-alerting deployments continue normally.
    """
    topic_arn = os.environ.get("INCIDENT_ALERT_TOPIC_ARN")
    if not topic_arn:
        return False

    severity = incident.get("severity")
    if severity not in ALERTABLE_SEVERITIES:
        return False

    alarm_name = incident.get("alarmName", "unknown-alarm")
    subject = f"SIRP {severity} Incident: {alarm_name}"
    message = "\n".join(
        [
            f"Incident ID: {incident.get('id')}",
            f"Title: {incident.get('title')}",
            f"Severity: {severity}",
            f"Status: {incident.get('status')}",
            f"Service: {incident.get('service')}",
            f"Alarm Name: {alarm_name}",
            f"Alarm State: {incident.get('alarmState')}",
            f"Alarm Timestamp: {incident.get('alarmTimestamp')}",
        ]
    )

    _sns_client().publish(
        TopicArn=topic_arn,
        Subject=subject,
        Message=message,
    )
    return True
