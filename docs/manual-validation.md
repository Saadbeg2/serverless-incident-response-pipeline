# Manual Validation

This document records the manual AWS validation completed for the Serverless Incident Response Pipeline project.

## Purpose

The purpose of manual validation was to prove that the Phase 1 Lambda handler logic could run in AWS against a real DynamoDB table.

Initial validation was not a full production deployment. API Gateway, EventBridge, real CloudWatch alarms, and alarm automation were not deployed at first; CloudWatch-style alarm events were tested manually through Lambda test events. A later phase added a controlled CloudWatch alarm and EventBridge trigger path using a failure simulator Lambda.

## Why Build Manually Before CloudFormation

The backend was first built manually to understand the AWS service boundaries before codifying the setup in CloudFormation/SAM.

Manual validation helped confirm:

- How Lambda loads the packaged Python handlers.
- How Lambda uses the `INCIDENTS_TABLE_NAME` environment variable.
- Which DynamoDB permissions the functions need.
- Which IAM and S3 permissions are required for a simple deployment flow.
- Which timeout and memory settings are practical for the functions.

The intended repeatable deployment method remains CloudFormation/SAM.

## Resources Created

- S3 artifact bucket: `sirp-lambda-artifacts-dev-saad-20260621`
- Lambda deployment artifact: `lambda-package.zip`
- DynamoDB table: `sirp-incidents-dev`
- SNS topic: `sirp-incident-alerts-dev`
- SNS topic ARN: `arn:aws:sns:us-east-1:107570341596:sirp-incident-alerts-dev`
- Confirmed SNS email subscription
- IAM user used for manual build: `SIRP`
- IAM Lambda execution role: `sirp-lambda-role-dev`
- Inline Lambda role policy: `sirp-lambda-dynamodb-logs-policy`
- Lambda functions:
  - `sirp-create-incident-dev`
  - `sirp-get-incident-dev`
  - `sirp-list-incidents-dev`
  - `sirp-update-incident-dev`
  - `sirp-alarm-to-incident-dev`
  - `sirp-escalate-incidents-dev`

## Lambda Configuration

| Function | Handler | Runtime | Memory | Timeout | Environment |
|---|---|---:|---:|---:|---|
| `sirp-create-incident-dev` | `create_incident.handler` | Python 3.12 | 256 MB | 10 seconds | `INCIDENTS_TABLE_NAME=sirp-incidents-dev` |
| `sirp-get-incident-dev` | `get_incident.handler` | Python 3.12 | 256 MB | 10 seconds | `INCIDENTS_TABLE_NAME=sirp-incidents-dev` |
| `sirp-list-incidents-dev` | `list_incidents.handler` | Python 3.12 | 256 MB | 10 seconds | `INCIDENTS_TABLE_NAME=sirp-incidents-dev` |
| `sirp-update-incident-dev` | `update_incident.handler` | Python 3.12 | 256 MB | 10 seconds | `INCIDENTS_TABLE_NAME=sirp-incidents-dev` |
| `sirp-alarm-to-incident-dev` | `alarm_to_incident.handler` | Python 3.12 | 256 MB | 10 seconds | `INCIDENTS_TABLE_NAME=sirp-incidents-dev` |
| `sirp-escalate-incidents-dev` | `escalate_incidents.handler` | Python 3.12 | 256 MB | 10 seconds | `INCIDENTS_TABLE_NAME=sirp-incidents-dev` |

Shared configuration:

- Execution role: `sirp-lambda-role-dev`
- Code source: `s3://sirp-lambda-artifacts-dev-saad-20260621/lambda-package.zip`

## SNS Validation

SNS was validated manually before wiring Lambda alert publishing into the code.

Validation steps:

- Created SNS topic `sirp-incident-alerts-dev`.
- Confirmed an email subscription to the topic.
- Published a manual test alert to the topic.
- Received the test email from `no-reply@sns.amazonaws.com`.

This proved that SNS notification delivery worked before connecting the `alarm_to_incident` Lambda to publish alerts. Real CloudWatch alarms are still not connected; CloudWatch-style alarm events are manually tested through Lambda test events.

## SNS-Enabled Alarm-to-Incident Validation

After SNS alert publishing was added to the `alarm_to_incident` Lambda code, the latest package was manually validated in AWS.

Validation steps:

- Uploaded the updated `lambda-package.zip` to `s3://sirp-lambda-artifacts-dev-saad-20260621/lambda-package.zip`.
- Updated `sirp-alarm-to-incident-dev` from the latest S3 package.
- Ran a new CloudWatch-style Lambda test event.

Test event details:

- `alarmName`: `checkout-api-high-5xx-sns-test`
- `timestamp`: `2026-06-22T18:30:00Z`

Results:

- Lambda returned `statusCode` `201`.
- DynamoDB stored a new incident:
  - `id`: `alarm-06aef43378caa053`
  - `severity`: `HIGH`
  - `status`: `OPEN`
  - `source`: `cloudwatch`
- SNS email alert was successfully received.

This was still a manual Lambda test event using a CloudWatch-style payload. A real CloudWatch alarm trigger is not connected yet.

## SAM/CloudFormation Deployment Validation

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
- CloudWatch log groups for each Lambda.
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
- Created incident:
  - `id`: `alarm-90eb8d0c5dedab14`
  - `severity`: `HIGH`
  - `status`: `OPEN`
  - `source`: `cloudwatch`
- SNS email alert was received successfully.

This was still a manual Lambda test event using a CloudWatch-style payload. A real CloudWatch alarm trigger is not connected yet.

## Real CloudWatch Alarm Trigger Path

The project now includes a low-cost failure simulation path so validation does not depend only on manual Lambda test events.

Planned validation flow:

1. Invoke `sirp-failure-simulator-sam-dev`.
2. The function logs a clear message and intentionally raises an exception.
3. CloudWatch records a Lambda `Errors` metric.
4. CloudWatch alarm `sirp-failure-simulator-errors-sam-dev` enters `ALARM`.
5. EventBridge rule `sirp-failure-simulator-alarm-rule-sam-dev` captures the CloudWatch Alarm State Change event.
6. EventBridge invokes `sirp-alarm-to-incident-sam-dev`.
7. The alarm-to-incident Lambda creates an incident in `sirp-incidents-sam-dev`.
8. The SNS alert path sends an email for the HIGH severity incident.

This path uses only serverless, usage-based services. It does not add API Gateway, EC2, RDS, NAT Gateway, ALB, ECS, or always-running compute.

## Real CloudWatch Alarm Trigger Validation

The fully automated flow was successfully validated:

```text
sirp-failure-simulator-sam-dev intentionally failed
  -> CloudWatch Lambda Errors metric was recorded
  -> CloudWatch alarm sirp-failure-simulator-errors-sam-dev entered ALARM
  -> EventBridge rule sirp-failure-simulator-alarm-rule-sam-dev matched the CloudWatch Alarm State Change event
  -> sirp-alarm-to-incident-sam-dev was invoked automatically
  -> DynamoDB table sirp-incidents-sam-dev stored a new incident
  -> SNS email alert was received
```

Failure simulator invoke returned:

- `StatusCode`: `200`
- `FunctionError`: `Unhandled`
- `RuntimeError: Intentional failure generated for SIRP CloudWatch alarm test.`

DynamoDB confirmed incident:

- `id`: `alarm-8a107dc637b96a30`
- `alarmName`: `sirp-failure-simulator-errors-sam-dev`
- `severity`: `HIGH`
- `status`: `OPEN`
- `source`: `cloudwatch`
- `alarmState`: `ALARM`
- `createdAt`: `2026-06-23T16:47:27Z`

The SNS email alert was received successfully, with a slight delay after the simulator failure.

Deployment lesson:

- Local `sam validate` only confirms the template is valid.
- Real deployment can still fail if the deploy IAM user lacks permissions for generated or named resources.
- The project fixed this by using predictable SAM resource names and updating deploy permissions.

## Test Results Summary

| Test | Result |
|---|---|
| `create_incident` | Created a manual incident titled `API latency spike`; response `statusCode` was `201`; item appeared in DynamoDB. |
| `get_incident` | Retrieved the created incident by `incidentId`; response `statusCode` was `200`. |
| `list_incidents` | Listed incidents from DynamoDB; response `statusCode` was `200`; existing incident was returned. |
| `update_incident` | Updated incident status from `OPEN` to `INVESTIGATING`; response `statusCode` was `200`; item updated in DynamoDB. |
| `alarm_to_incident` | Created an incident from a CloudWatch-style alarm event with id `alarm-89e60cafabdceb89`; stored `alarmName` was `checkout-api-high-5xx`. |
| `alarm_to_incident` idempotency | Ran the same exact alarm event twice and confirmed the same incident id was returned. |
| SNS manual publish | Published a manual SNS test alert and confirmed email delivery. |
| SNS-enabled `alarm_to_incident` | Updated `sirp-alarm-to-incident-dev` from the latest S3 package, ran `checkout-api-high-5xx-sns-test`, created incident `alarm-06aef43378caa053`, and received the SNS email alert. |
| SAM-deployed SNS-enabled `alarm_to_incident` | Deployed stack `sirp-dev`, ran `checkout-api-high-5xx-sam-test` against `sirp-alarm-to-incident-sam-dev`, created incident `alarm-90eb8d0c5dedab14`, and received the SNS email alert. |
| Real CloudWatch alarm trigger | Invoked `sirp-failure-simulator-sam-dev`, CloudWatch alarm `sirp-failure-simulator-errors-sam-dev` entered `ALARM`, EventBridge invoked `sirp-alarm-to-incident-sam-dev`, incident `alarm-8a107dc637b96a30` was stored, and SNS email was received. |
| `escalate_incidents` | Tested with `cutoffTimestamp` set to `2027-01-01T00:00:00Z`; response `statusCode` was `200`; escalated 3 stale `OPEN` alarm incidents. |

## Troubleshooting Notes

- Initial Lambda timeout was 3 seconds and caused `Sandbox.Timeout` errors.
- Timeout issues were fixed by setting memory to 256 MB and timeout to 10 seconds.
- Early alarm tests used the wrong event shape, which created `unknown-alarm` records.
- Alarm tests were fixed by using the correct CloudWatch Alarm State Change shape from `events/alarm_event.json`.
- S3 bucket creation initially failed because the `SIRP` user was missing permissions for default encryption and bucket tagging.
- S3 setup was fixed by adding permissions for encryption configuration and tagging.
- IAM console navigation required `ListRoles` and `ListPolicies` for the `SIRP` user, while resource creation remained scoped to `sirp-*` where possible.
- An S3 object tag warning appeared during upload but did not block the project.

## Lessons Learned

- Lambda timeout and memory settings should be tested with the real AWS runtime, not only locally.
- The exact event shape matters, especially for CloudWatch alarm-style events.
- Idempotency is important because repeated alarm events should not create duplicate incident records.
- IAM permissions need to cover both runtime behavior and practical console navigation during manual validation.
- Packaging only the Lambda source files keeps deployment artifacts smaller and easier to reason about.

## What This Proved

Manual validation proved that:

- The Lambda handlers can run in AWS with Python 3.12.
- The handlers can use DynamoDB when `INCIDENTS_TABLE_NAME` is set.
- Incidents can be created, retrieved, listed, updated, generated from alarm-style events, and escalated.
- Deterministic alarm incident ids prevent duplicate records for the same alarm event.
- SNS can deliver email notifications from a manually published alert.
- The alarm-to-incident Lambda can publish an SNS email alert for a manually tested HIGH CloudWatch-style incident.
- The same SNS-enabled alarm-to-incident path can be deployed repeatably with SAM/CloudFormation.
- A real CloudWatch alarm state change can be produced with a failure simulator Lambda and routed through EventBridge to the existing alarm-to-incident Lambda.
- The complete automated path from Lambda failure to incident record to SNS email works.
- The backend now has a real failure-simulator alarm path without API Gateway or always-running compute.
