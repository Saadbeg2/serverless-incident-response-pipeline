# Architecture Diagram

```text
CloudWatch Alarm
      |
      v
     SNS
      |
      v
Alarm-to-Incident Lambda
      |
      v
  DynamoDB Incidents Table

API Gateway
      |
      v
Incident API Lambdas
      |
      v
  DynamoDB Incidents Table

EventBridge Schedule
      |
      v
Escalation Lambda
      |
      v
  DynamoDB Incidents Table
```

This diagram is a placeholder for the planned architecture. A more detailed visual diagram can be added after the AWS resources are implemented.
