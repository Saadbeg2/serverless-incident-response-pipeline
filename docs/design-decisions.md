# Design Decisions

This document will track the reasoning behind major architecture choices.

## Why Serverless

Placeholder: Explain why Lambda, API Gateway, DynamoDB, SNS, and EventBridge are a good fit for a low-cost incident response project.

## Why DynamoDB

Placeholder: Explain why DynamoDB is planned for incident records, including simple access patterns and pay-per-request pricing.

## Why CloudFormation

Placeholder: Explain why infrastructure should be defined with CloudFormation or AWS SAM instead of being created manually.

## Manual Validation Before Infrastructure as Code

The architecture was first built and validated manually in AWS to understand the service boundaries between Lambda, S3, IAM, DynamoDB, and CloudWatch Logs.

Manual validation helped prove that the Lambda handlers could run in AWS, use the `INCIDENTS_TABLE_NAME` environment variable, read and write DynamoDB records, and handle CloudWatch-style alarm events through Lambda test events.

After validating the workflow manually, the next step is to codify the same setup in CloudFormation/SAM so it can be recreated consistently and torn down safely.

## Why Idempotency Matters

CloudWatch alarm events may be delivered more than once, retried, or triggered repeatedly if an alarm flaps between states. Without idempotency, the pipeline could create multiple incident records for the same alarm state change.

For Phase 1, `alarm_to_incident.py` uses a deterministic incident id based on the alarm name and state-change timestamp. If the same event is handled twice, the in-memory store returns the existing incident instead of creating a duplicate.

## Why Local In-Memory Tests Come First

Local tests make the Lambda logic easy to understand and safe to change before any AWS resources exist.

The project uses an in-memory incident store during Phase 1 so tests can run without AWS credentials, network access, or paid infrastructure. This keeps the feedback loop fast while leaving a clear path to replace the storage internals with DynamoDB in a later phase.

## Why Least-Privilege IAM Matters

Placeholder: Explain why each Lambda function should only receive the permissions it needs.

## Why SNS Was Added

SNS was added so high-severity incident events can notify operators by email instead of only writing records to DynamoDB.

The project originally stored incidents in DynamoDB. SNS adds a simple alerting path while keeping the architecture serverless and low-cost.

## Why Alerting Is Limited to HIGH and CRITICAL

Only `HIGH` and `CRITICAL` incidents publish SNS alerts. This avoids noisy emails for lower-severity events and keeps alerting focused on incidents that need faster operator attention.

## Why SNS Publishing Is Environment-Variable Controlled

SNS publishing depends on `INCIDENT_ALERT_TOPIC_ARN`. If the variable is not set, the Lambda still creates incidents but skips alert publishing.

This keeps local tests simple, avoids requiring AWS credentials, and allows the same code to run in non-alerting environments.

## Why SNS Was Manually Validated First

SNS was manually validated before code integration to prove that the topic, email subscription, and delivery path worked independently.

After confirming manual SNS publish delivered an email, the `alarm_to_incident` Lambda could be connected to SNS with a small code change and a least-privilege `sns:Publish` permission.
