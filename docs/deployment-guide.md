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
- Seven Lambda functions, including a failure simulator for alarm validation.
- One CloudWatch alarm on the failure simulator Lambda `Errors` metric.
- One EventBridge rule that sends the alarm state change event to `alarm_to_incident`.
- Least-privilege IAM permissions for those functions.
- CloudWatch log groups with 7-day retention.

This phase does not deploy API Gateway or create the SNS topic. It can use an existing SNS topic ARN for alerts.

## Manual AWS Deployment Path

The backend was manually validated before being codified for repeatable CloudFormation/SAM deployment. This path is useful for learning how the AWS service boundaries fit together, but CloudFormation/SAM remains the intended long-term deployment method.

High-level manual steps:

1. Package Lambda code.

   Create a zip file containing the Python handler files from `src/` so handlers such as `create_incident.handler` are at the package root.

2. Upload zip to S3.

   Upload the artifact as `lambda-package.zip` to the deployment artifact bucket.

3. Create the DynamoDB table.

   Create a table named `sirp-incidents-dev` with partition key `id`.

4. Create the Lambda execution role.

   Create `sirp-lambda-role-dev` and allow Lambda to assume it.

5. Attach an inline policy.

   Attach `sirp-lambda-dynamodb-logs-policy` with DynamoDB access to the incidents table and permissions to write CloudWatch logs.

6. Create Lambda functions.

   Create:

   - `sirp-create-incident-dev`
   - `sirp-get-incident-dev`
   - `sirp-list-incidents-dev`
   - `sirp-update-incident-dev`
   - `sirp-alarm-to-incident-dev`
   - `sirp-escalate-incidents-dev`

7. Upload code from S3.

   Use `s3://sirp-lambda-artifacts-dev-saad-20260621/lambda-package.zip` as the code source.

8. Set handler and environment variables.

   Configure each function with Python 3.12, 256 MB memory, 10 second timeout, and `INCIDENTS_TABLE_NAME=sirp-incidents-dev`.

   | Function | Handler |
   |---|---|
   | `sirp-create-incident-dev` | `create_incident.handler` |
   | `sirp-get-incident-dev` | `get_incident.handler` |
   | `sirp-list-incidents-dev` | `list_incidents.handler` |
   | `sirp-update-incident-dev` | `update_incident.handler` |
   | `sirp-alarm-to-incident-dev` | `alarm_to_incident.handler` |
   | `sirp-escalate-incidents-dev` | `escalate_incidents.handler` |

9. Test functions.

   Use Lambda test events for create, get, list, update, alarm-to-incident, and escalation flows.

10. Verify DynamoDB records.

   Confirm incidents are created and updated in the `sirp-incidents-dev` table.

See [manual-validation.md](manual-validation.md) for the validation record and lessons learned.

## Manual SNS Alert Update Path

After adding SNS alert publishing to `alarm_to_incident`, update only the alarm-to-incident Lambda during manual validation.

Recreate the Lambda zip:

```bash
cd src
zip -r ../lambda-package.zip .
cd ..
```

Upload the new zip to the existing artifact location:

```bash
aws s3 cp lambda-package.zip \
  s3://sirp-lambda-artifacts-dev-saad-20260621/lambda-package.zip
```

Update the existing Lambda function code from S3:

```bash
aws lambda update-function-code \
  --function-name sirp-alarm-to-incident-dev \
  --s3-bucket sirp-lambda-artifacts-dev-saad-20260621 \
  --s3-key lambda-package.zip
```

Add the SNS topic ARN to the alarm-to-incident Lambda environment, alongside the existing DynamoDB table variable:

```bash
aws lambda update-function-configuration \
  --function-name sirp-alarm-to-incident-dev \
  --environment "Variables={INCIDENTS_TABLE_NAME=sirp-incidents-dev,INCIDENT_ALERT_TOPIC_ARN=arn:aws:sns:us-east-1:107570341596:sirp-incident-alerts-dev}"
```

Update the Lambda execution role inline policy so only the alarm-to-incident function role can publish to the alert topic:

```json
{
  "Sid": "PublishIncidentAlerts",
  "Effect": "Allow",
  "Action": [
    "sns:Publish"
  ],
  "Resource": "arn:aws:sns:us-east-1:107570341596:sirp-incident-alerts-dev"
}
```

Then test `sirp-alarm-to-incident-dev` with a CloudWatch-style Lambda test event and confirm:

- The incident is created or returned from DynamoDB.
- HIGH or CRITICAL incidents publish an SNS alert.
- The confirmed subscription receives the email.
- Running the same exact event again returns the same incident id and should not send a duplicate alert.

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
  --stack-name sirp-dev
```

During guided deployment, review the generated changes carefully before confirming.

## SAM Deployment Validation

The project was successfully deployed with AWS SAM/CloudFormation using stack name `sirp-dev`.

CloudFormation created:

- DynamoDB table: `sirp-incidents-sam-dev`
- Lambda functions:
  - `sirp-create-incident-sam-dev`
  - `sirp-get-incident-sam-dev`
  - `sirp-list-incidents-sam-dev`
  - `sirp-update-incident-sam-dev`
  - `sirp-alarm-to-incident-sam-dev`
  - `sirp-escalate-incidents-sam-dev`
- CloudWatch log groups for each Lambda function.
- Lambda execution IAM roles.

Post-deploy validation checked `sirp-alarm-to-incident-sam-dev` configuration:

- Runtime: `python3.12`
- Timeout: `10`
- Memory: `256`
- `INCIDENTS_TABLE_NAME=sirp-incidents-sam-dev`
- `INCIDENT_ALERT_TOPIC_ARN=arn:aws:sns:us-east-1:107570341596:sirp-incident-alerts-dev`

The function was invoked with a CloudWatch-style Lambda test event:

- `alarmName`: `checkout-api-high-5xx-sam-test`
- `timestamp`: `2026-06-23T01:30:00Z`

Results:

- AWS invoke `StatusCode`: `200`
- Application `statusCode`: `201`
- Created incident id: `alarm-90eb8d0c5dedab14`
- Incident fields: `severity=HIGH`, `status=OPEN`, `source=cloudwatch`
- SNS email alert received successfully.

This was still manually tested with a CloudWatch-style Lambda test event. A real CloudWatch alarm trigger is not connected yet.

## Failure Simulator Alarm Validation

The deployable stack now includes a real low-cost alarm trigger path:

```text
sirp-failure-simulator-sam-dev
  -> Lambda Errors metric
  -> sirp-failure-simulator-errors-sam-dev CloudWatch alarm
  -> sirp-failure-simulator-alarm-rule-sam-dev EventBridge rule
  -> sirp-alarm-to-incident-sam-dev
  -> DynamoDB incident
  -> SNS email alert
```

To validate after deployment:

1. Invoke `sirp-failure-simulator-sam-dev`.
2. Confirm it fails intentionally.
3. Wait for CloudWatch to evaluate the Lambda `Errors` metric.
4. Confirm alarm `sirp-failure-simulator-errors-sam-dev` enters `ALARM`.
5. Confirm EventBridge invokes `sirp-alarm-to-incident-sam-dev`.
6. Confirm DynamoDB table `sirp-incidents-sam-dev` stores a new incident.
7. Confirm the SNS email alert is received.

The failure simulator exists only to generate CloudWatch `Errors` metrics for this validation path.

This fully automated flow was successfully validated:

```text
sirp-failure-simulator-sam-dev intentionally failed
  -> CloudWatch Lambda Errors metric was recorded
  -> sirp-failure-simulator-errors-sam-dev entered ALARM
  -> sirp-failure-simulator-alarm-rule-sam-dev matched the alarm state change
  -> sirp-alarm-to-incident-sam-dev was invoked automatically
  -> sirp-incidents-sam-dev stored a new incident
  -> SNS email alert was received
```

Failure simulator invoke result:

- `StatusCode`: `200`
- `FunctionError`: `Unhandled`
- Error: `RuntimeError: Intentional failure generated for SIRP CloudWatch alarm test.`

DynamoDB confirmed incident:

- `id`: `alarm-8a107dc637b96a30`
- `alarmName`: `sirp-failure-simulator-errors-sam-dev`
- `severity`: `HIGH`
- `status`: `OPEN`
- `source`: `cloudwatch`
- `alarmState`: `ALARM`
- `createdAt`: `2026-06-23T16:47:27Z`

The SNS email alert was received, with a slight delay after the simulator failure while CloudWatch evaluated the metric and EventBridge delivered the alarm state change.

## Deploy IAM Permissions For Alarm Trigger Path

The deploy user needs permissions for the new CloudWatch alarm, EventBridge rule, Lambda invoke permission, and failure simulator Lambda resources.

Recommended resource patterns:

- CloudWatch alarm: `arn:aws:cloudwatch:us-east-1:<account-id>:alarm:sirp-*`
- EventBridge rule: `arn:aws:events:us-east-1:<account-id>:rule/sirp-*`
- Lambda functions: `arn:aws:lambda:us-east-1:<account-id>:function:sirp-*`
- CloudWatch log groups: `arn:aws:logs:us-east-1:<account-id>:log-group:/aws/lambda/sirp-*`

Useful actions:

- CloudWatch alarms: `cloudwatch:PutMetricAlarm`, `cloudwatch:DeleteAlarms`, `cloudwatch:DescribeAlarms`, `cloudwatch:TagResource`, `cloudwatch:UntagResource`
- EventBridge: `events:PutRule`, `events:DeleteRule`, `events:DescribeRule`, `events:PutTargets`, `events:RemoveTargets`, `events:ListTargetsByRule`, `events:TagResource`, `events:UntagResource`
- Lambda permissions: `lambda:AddPermission`, `lambda:RemovePermission`, `lambda:GetPolicy`
- Optional debugging only: `cloudwatch:GetMetricStatistics`

Deployment lesson:

- Local `sam validate` confirms that the template is valid.
- Real deployment can still fail if the deploy IAM user lacks permissions for generated or named resources.
- This project fixed that by using predictable SAM resource names and updating deploy permissions.

## Check Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name sirp-dev \
  --query "Stacks[0].Outputs"
```

The outputs include the DynamoDB table name and Lambda function names.

## Delete the Stack

Use this exact command when you are done testing:

```bash
aws cloudformation delete-stack \
  --stack-name sirp-dev
```

Then confirm deletion completed:

```bash
aws cloudformation wait stack-delete-complete \
  --stack-name sirp-dev
```

## Teardown-First Reminder

Before deploying, confirm AWS budget alerts are active. After testing, delete the stack so Lambda functions, IAM roles, the DynamoDB table, and log groups are removed.
