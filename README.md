# Serverless Incident Response Pipeline

## Problem Statement

Cloud incidents often start as monitoring alarms, but teams still need a reliable way to turn those alarms into trackable incident records. Without a simple pipeline, alerts can be missed, duplicated, or handled without a clear audit trail.

This project is a resume-focused AWS cloud engineering project that demonstrates how to design a low-cost, serverless incident response workflow.

## High-Level Solution

The planned system will listen for CloudWatch alarms, create incident records, send alerts, and expose an API so engineers can view and update incident status.

The current version implements local, testable Lambda handler logic and deployable AWS infrastructure for Lambda, DynamoDB, SNS alert publishing, and a low-cost CloudWatch alarm trigger path. API Gateway is planned for a later phase.

## Planned Architecture

The project is planned around three serverless flows:

1. Failure Simulator Lambda -> CloudWatch Alarm -> EventBridge -> Lambda -> DynamoDB -> SNS
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
- SAM/CloudFormation deployment validation: Complete. Stack `sirp-dev` deployed the SAM-managed DynamoDB table, Lambda functions, CloudWatch log groups, and Lambda execution IAM roles. `sirp-alarm-to-incident-sam-dev` was validated with a CloudWatch-style Lambda test event and delivered an SNS email alert.
- Real alarm trigger path: Added. A failure simulator Lambda can intentionally fail, CloudWatch alarms on its `Errors` metric, EventBridge routes the alarm state change to `alarm_to_incident`, and the existing pipeline creates a DynamoDB incident and sends an SNS alert.
- Real CloudWatch alarm validation: Complete. `sirp-failure-simulator-sam-dev` intentionally failed, CloudWatch alarm `sirp-failure-simulator-errors-sam-dev` entered `ALARM`, EventBridge invoked `sirp-alarm-to-incident-sam-dev`, DynamoDB stored incident `alarm-8a107dc637b96a30`, and an SNS email alert was received.

Manual validation confirmed that incidents can be created, retrieved, listed, updated, created from CloudWatch-style alarm events, escalated when stale, and sent as SNS email alerts for high-severity alarm-style incidents. SNS manual publish was also validated. API Gateway is not deployed yet.

The project now includes a validated real CloudWatch alarm and EventBridge trigger path for the failure simulator flow. Existing CloudWatch-style Lambda test events remain useful for focused handler testing.

See [docs/manual-validation.md](docs/manual-validation.md) for the validation summary.

Deployment is optional and manual. Local tests still do not require AWS credentials. CloudFormation/SAM is now the validated repeatable deployment method, but real deployment still depends on the deploy IAM user having permissions for the named stack resources.

## Teardown-First Mindset

Every future AWS resource should be created through infrastructure as code and should have a clear teardown path. The goal is to make experimentation safe, repeatable, and inexpensive.
