# Design Decisions

This document will track the reasoning behind major architecture choices.

## Why Serverless

Placeholder: Explain why Lambda, API Gateway, DynamoDB, SNS, and EventBridge are a good fit for a low-cost incident response project.

## Why DynamoDB

Placeholder: Explain why DynamoDB is planned for incident records, including simple access patterns and pay-per-request pricing.

## Why CloudFormation

Placeholder: Explain why infrastructure should be defined with CloudFormation or AWS SAM instead of being created manually.

## Why Idempotency Matters

CloudWatch alarm events may be delivered more than once, retried, or triggered repeatedly if an alarm flaps between states. Without idempotency, the pipeline could create multiple incident records for the same alarm state change.

For Phase 1, `alarm_to_incident.py` uses a deterministic incident id based on the alarm name and state-change timestamp. If the same event is handled twice, the in-memory store returns the existing incident instead of creating a duplicate.

## Why Local In-Memory Tests Come First

Local tests make the Lambda logic easy to understand and safe to change before any AWS resources exist.

The project uses an in-memory incident store during Phase 1 so tests can run without AWS credentials, network access, or paid infrastructure. This keeps the feedback loop fast while leaving a clear path to replace the storage internals with DynamoDB in a later phase.

## Why Least-Privilege IAM Matters

Placeholder: Explain why each Lambda function should only receive the permissions it needs.
