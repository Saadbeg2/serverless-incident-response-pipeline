# Deployment Guide

This guide explains how to manually deploy the Phase 2 backend.

Deployment is optional. Local tests do not require AWS credentials.

## Prerequisites

- An AWS account you are allowed to use for learning projects.
- AWS budget alerts enabled before deployment.
- AWS CLI installed and configured.
- AWS SAM CLI installed.
- Permission to create CloudFormation stacks, Lambda functions, IAM roles, DynamoDB tables, and CloudWatch log groups.

## What This Phase Deploys

Phase 2 deploys:

- One DynamoDB table for incident records.
- Six Lambda functions.
- Least-privilege IAM permissions for those functions.
- CloudWatch log groups with 7-day retention.

This phase does not deploy API Gateway, SNS, EventBridge, or CloudWatch alarm automation.

## Validate the Template

From the repository root, run:

```bash
sam validate --lint --template-file template.yaml
```

If `sam validate --lint` is not available in your SAM CLI version, run:

```bash
sam validate --template-file template.yaml
```

## Deploy Manually

Use a clear stack name so teardown is easy:

```bash
sam deploy \
  --guided \
  --stack-name serverless-incident-response-pipeline
```

During guided deployment, review the generated changes carefully before confirming.

## Check Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name serverless-incident-response-pipeline \
  --query "Stacks[0].Outputs"
```

The outputs include the DynamoDB table name and Lambda function names.

## Delete the Stack

Use this exact command when you are done testing:

```bash
aws cloudformation delete-stack \
  --stack-name serverless-incident-response-pipeline
```

Then confirm deletion completed:

```bash
aws cloudformation wait stack-delete-complete \
  --stack-name serverless-incident-response-pipeline
```

## Teardown-First Reminder

Before deploying, confirm AWS budget alerts are active. After testing, delete the stack so Lambda functions, IAM roles, the DynamoDB table, and log groups are removed.
