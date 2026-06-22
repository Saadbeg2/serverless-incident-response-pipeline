# Interview Notes

## 30-Second Explanation

This project is a low-cost, serverless incident response pipeline on AWS. The goal is to turn CloudWatch alarms into incident records, notify engineers, and expose an API for viewing and updating incidents. It uses services like Lambda, DynamoDB, SNS, API Gateway, EventBridge, IAM, and CloudFormation/SAM.

## 2-Minute Explanation

The project is designed to show practical AWS cloud engineering skills around event-driven architecture, serverless design, infrastructure as code, and operational thinking.

The planned flow starts with CloudWatch alarms. When an alarm fires, it publishes to SNS, which invokes a Lambda function. That function creates or updates an incident record in DynamoDB. Engineers can then use an API Gateway-backed API to list, read, create, or update incidents. A scheduled EventBridge rule will later invoke another Lambda function to find stale or unresolved incidents and support escalation logic.

The project is intentionally cost-conscious. It avoids always-on services like EC2, RDS, ECS, ALB, NAT Gateway, and Transit Gateway. Everything should be deployed and torn down through infrastructure as code.

## Manual Validation Explanation

I first built and validated the architecture manually in AWS to understand how Lambda, S3, IAM, DynamoDB, and CloudWatch Logs interacted. After validating the workflow manually, the next step is to codify the same setup in CloudFormation so it can be recreated consistently.

## SNS Alerting Explanation

The project originally stored incidents in DynamoDB. I then added SNS alerting so high-severity CloudWatch-style incidents could notify operators by email. I manually validated SNS first, then connected the alarm-to-incident Lambda to publish alerts through a least-privilege IAM permission.

## Likely Interview Questions

- Why did you choose a serverless architecture?
- How would you prevent duplicate incidents from repeated alarms?
- What DynamoDB access patterns would you design for?
- How would you secure the API?
- How would you design least-privilege IAM policies for each Lambda?
- How would you test this locally before deploying?
- How would you monitor and troubleshoot the pipeline itself?
- How would you keep this project low-cost?

## Draft Resume Bullets

- Designed a serverless incident response pipeline on AWS using Lambda, DynamoDB, SNS, API Gateway, EventBridge, IAM, and CloudFormation/SAM.
- Planned an event-driven workflow to convert CloudWatch alarms into trackable incident records.
- Documented cost-control and teardown practices to avoid always-on AWS infrastructure.
- Created a portfolio-ready project structure with testing, deployment, architecture, and troubleshooting documentation.
