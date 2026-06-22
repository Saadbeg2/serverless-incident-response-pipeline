# Serverless Incident Response Pipeline

## Problem Statement

Cloud incidents often start as monitoring alarms, but teams still need a reliable way to turn those alarms into trackable incident records. Without a simple pipeline, alerts can be missed, duplicated, or handled without a clear audit trail.

This project is a resume-focused AWS cloud engineering project that demonstrates how to design a low-cost, serverless incident response workflow.

## High-Level Solution

The planned system will listen for CloudWatch alarms, create incident records, send alerts, and expose an API so engineers can view and update incident status.

The current version implements local, testable Lambda handler logic and optional deployable AWS infrastructure for Lambda plus DynamoDB. SNS alerting has been manually validated and alarm-to-incident SNS publishing is being added for high-severity CloudWatch-style incidents. API Gateway, EventBridge, and real CloudWatch alarm automation are planned for later phases.

## Planned Architecture

The project is planned around three serverless flows:

1. CloudWatch Alarm -> SNS -> Lambda -> DynamoDB
2. API Gateway -> Lambda -> DynamoDB
3. EventBridge -> Lambda -> DynamoDB

## AWS Services Used

Planned AWS services include:

- Amazon CloudWatch
- Amazon SNS
- AWS Lambda
- Amazon DynamoDB
- Amazon API Gateway
- Amazon EventBridge
- AWS IAM
- AWS CloudFormation / AWS SAM

## Cost-Control Note

The project is designed to stay low-cost by using serverless services and avoiding always-on infrastructure. It will not use EC2, RDS, ECS, ALB, NAT Gateway, or Transit Gateway.

## Current Project Status

Status: Manual AWS validation complete after Phase 2.

- Phase 0: Complete. Initial repository scaffolding and documentation skeletons are in place.
- Phase 1: Complete. Local Lambda logic and unit tests are in place. Handlers can create, list, get, update, and escalate incidents using an in-memory store.
- Phase 2: Complete. SAM infrastructure now defines DynamoDB, deployable Lambda functions, least-privilege table permissions, and short-retention CloudWatch log groups.
- Manual AWS validation: Complete. Lambda functions were manually packaged, uploaded through S3, connected to DynamoDB, and tested with Lambda test events.
- Manual SNS validation: Complete. An SNS topic and confirmed email subscription were tested with a manual publish.
- SNS-enabled alarm-to-incident validation: Complete. The updated `lambda-package.zip` was uploaded to S3, `sirp-alarm-to-incident-dev` was updated from the latest package, and a CloudWatch-style Lambda test event created a HIGH incident in DynamoDB and delivered an SNS email alert.

Manual validation confirmed that incidents can be created, retrieved, listed, updated, created from CloudWatch-style alarm events, escalated when stale, and sent as SNS email alerts for high-severity alarm-style incidents. SNS manual publish was also validated. Real API Gateway, EventBridge, and CloudWatch alarm automation are not deployed yet.

CloudWatch-style alarm events are still manually tested through Lambda test events; real CloudWatch alarms are not connected yet.

See [docs/manual-validation.md](docs/manual-validation.md) for the validation summary.

Deployment is optional and manual. Local tests still do not require AWS credentials. CloudFormation/SAM remains the intended repeatable deployment method after manual validation.

## Teardown-First Mindset

Every future AWS resource should be created through infrastructure as code and should have a clear teardown path. The goal is to make experimentation safe, repeatable, and inexpensive.
