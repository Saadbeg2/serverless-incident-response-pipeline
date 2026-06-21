# Design Decisions

This document will track the reasoning behind major architecture choices.

## Why Serverless

Placeholder: Explain why Lambda, API Gateway, DynamoDB, SNS, and EventBridge are a good fit for a low-cost incident response project.

## Why DynamoDB

Placeholder: Explain why DynamoDB is planned for incident records, including simple access patterns and pay-per-request pricing.

## Why CloudFormation

Placeholder: Explain why infrastructure should be defined with CloudFormation or AWS SAM instead of being created manually.

## Why Idempotency Matters

Placeholder: Explain how duplicate alarms or retries could create duplicate incidents if handlers are not designed carefully.

## Why Least-Privilege IAM Matters

Placeholder: Explain why each Lambda function should only receive the permissions it needs.
