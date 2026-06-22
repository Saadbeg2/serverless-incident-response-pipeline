# Manual Validation

This document records the manual AWS validation completed for the Serverless Incident Response Pipeline project.

## Purpose

The purpose of manual validation was to prove that the Phase 1 Lambda handler logic could run in AWS against a real DynamoDB table.

This was not a full production deployment. API Gateway, EventBridge, real CloudWatch alarms, and alarm automation were not deployed. CloudWatch-style alarm events were tested manually through Lambda test events.

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
- The backend can work without API Gateway, EventBridge, or real CloudWatch alarm automation.
