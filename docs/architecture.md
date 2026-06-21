# Architecture

This document describes the planned architecture for the Serverless Incident Response Pipeline.

No AWS resources are implemented yet. The flows below describe the target design.

## Flow 1: CloudWatch Alarm -> SNS -> Lambda -> DynamoDB

CloudWatch alarms will detect operational issues such as high error rates, throttling, or elevated latency.

When an alarm enters the `ALARM` state, it will publish a message to an SNS topic. SNS will trigger a Lambda function that converts the alarm message into an incident record and stores it in DynamoDB.

Planned purpose:

- Automatically create incidents from monitoring signals.
- Reduce manual tracking work during an incident.
- Keep incident records in one table.

## Flow 2: API Gateway -> Lambda -> DynamoDB

API Gateway will expose endpoints for engineers to create, read, list, and update incidents.

Each API route will invoke a Lambda function. The function will validate the request, read or write incident data in DynamoDB, and return a JSON response.

Planned purpose:

- Allow engineers to view current incidents.
- Allow engineers to update status, severity, ownership, and notes.
- Keep the API serverless and inexpensive.

## Flow 3: EventBridge -> Lambda -> DynamoDB

EventBridge will run scheduled checks for incidents that need attention.

On a schedule, EventBridge will trigger a Lambda function that scans or queries incident records in DynamoDB. The function will identify incidents that may need escalation based on age, severity, or status.

Planned purpose:

- Find incidents that have not been acknowledged or resolved.
- Support future alerting or escalation logic.
- Demonstrate scheduled serverless automation.
