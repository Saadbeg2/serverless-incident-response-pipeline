# Serverless Incident Response Pipeline

## Problem Statement

Cloud incidents often start as monitoring alarms, but teams still need a reliable way to turn those alarms into trackable incident records. Without a simple pipeline, alerts can be missed, duplicated, or handled without a clear audit trail.

This project is a resume-focused AWS cloud engineering project that demonstrates how to design a low-cost, serverless incident response workflow.

## High-Level Solution

The planned system will listen for CloudWatch alarms, create incident records, send alerts, and expose an API so engineers can view and update incident status.

The current version implements local, testable Lambda handler logic and optional deployable AWS infrastructure for Lambda plus DynamoDB. API Gateway, SNS, EventBridge, and CloudWatch alarm automation are planned for later phases.

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

Status: Phase 2 complete.

- Phase 0: Complete. Initial repository scaffolding and documentation skeletons are in place.
- Phase 1: Complete. Local Lambda logic and unit tests are in place. Handlers can create, list, get, update, and escalate incidents using an in-memory store.
- Phase 2: Complete. SAM infrastructure now defines DynamoDB, deployable Lambda functions, least-privilege table permissions, and short-retention CloudWatch log groups.

Deployment is optional and manual. Local tests still do not require AWS credentials.

## Teardown-First Mindset

Every future AWS resource should be created through infrastructure as code and should have a clear teardown path. The goal is to make experimentation safe, repeatable, and inexpensive.
