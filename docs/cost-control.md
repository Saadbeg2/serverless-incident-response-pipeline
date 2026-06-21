# Cost Control

This project is designed for low-cost AWS learning and portfolio use.

## Services Intentionally Avoided

The project avoids infrastructure that can create steady or unexpected costs, including:

- EC2
- RDS
- ECS
- ALB
- NAT Gateway
- Transit Gateway
- OpenSearch

## Cost-Control Principles

- Prefer serverless services with free tier or usage-based pricing.
- Keep Lambda memory and timeout settings modest.
- Use DynamoDB carefully and start with small test data.
- Avoid always-on compute.
- Keep deployments easy to tear down.

## Phase 2 Resources

Phase 2 creates only low-cost serverless backend resources:

- One DynamoDB table using on-demand billing.
- Six Lambda functions with small memory and timeout settings.
- IAM roles and policies for Lambda access to DynamoDB.
- CloudWatch log groups with 7-day retention.

It does not create API Gateway, SNS, EventBridge schedules, CloudWatch alarms, or any always-running compute.

## Why This Should Be Low-Cost

DynamoDB uses `PAY_PER_REQUEST`, which is simple for low and unpredictable learning-project traffic. Lambda only charges when functions run. There are no servers, containers, load balancers, NAT gateways, databases, or search clusters running continuously.

Point-in-time recovery is skipped in this phase to keep the learning stack simple and avoid backup-related cost questions. It can be revisited later if the project needs stronger recovery guarantees.

## CloudWatch Log Retention

Each Lambda log group is configured with 7-day retention. Short retention keeps troubleshooting logs available during testing while limiting long-term log storage costs.

## Teardown Command

Delete the stack when you are done testing:

```bash
aws cloudformation delete-stack \
  --stack-name serverless-incident-response-pipeline
```

Confirm deletion completed:

```bash
aws cloudformation wait stack-delete-complete \
  --stack-name serverless-incident-response-pipeline
```
