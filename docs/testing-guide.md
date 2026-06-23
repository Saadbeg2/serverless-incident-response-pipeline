# Testing Guide

This guide explains how to test the project locally during Phase 1.

No AWS credentials are required. The tests do not deploy anything and do not call AWS services.

## Run Tests Locally

From the repository root, run:

```bash
python -m unittest discover -s tests
```

## Run a Compile Check

```bash
python -m compileall src tests
```

## Validate Event Fixtures

```bash
python -m json.tool events/alarm_event.json
python -m json.tool events/create_incident.json
python -m json.tool events/update_incident.json
```

## Local In-Memory Store

Phase 1 and Phase 2 local tests use `src/incident_store.py` as a small storage abstraction backed by an in-memory dictionary.

Local tests still use the in-memory dictionary because `INCIDENTS_TABLE_NAME` is not set during normal local test runs.

This lets the Lambda handlers be tested locally without AWS credentials, DynamoDB tables, or deployment steps. The store supports creating, reading, listing, updating, and finding stale open incidents.

The in-memory store resets when the Python process exits. Unit tests also clear it between test cases so each test starts from a known state.

## DynamoDB Runtime Behavior

When deployed by the Phase 2 SAM template, each Lambda receives the `INCIDENTS_TABLE_NAME` environment variable. When that variable is present, `src/incident_store.py` uses boto3 to read and write incidents in DynamoDB.

Do not set `INCIDENTS_TABLE_NAME` for regular unit tests unless you intentionally want to test against AWS.

## Manual AWS Test Events

These events were used through Lambda test events during manual AWS validation. Replace `example-incident-id` with a real incident id returned by `create_incident` before testing `get_incident` or `update_incident`.

### Create Incident

```json
{
  "httpMethod": "POST",
  "path": "/incidents",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"title\":\"API latency spike\",\"description\":\"The checkout API is responding slower than normal.\",\"severity\":\"high\",\"service\":\"checkout-api\"}"
}
```

### Get Incident

```json
{
  "httpMethod": "GET",
  "path": "/incidents/example-incident-id",
  "pathParameters": {
    "incidentId": "example-incident-id"
  }
}
```

### List Incidents

```json
{
  "httpMethod": "GET",
  "path": "/incidents",
  "queryStringParameters": null
}
```

To filter by status:

```json
{
  "httpMethod": "GET",
  "path": "/incidents",
  "queryStringParameters": {
    "status": "OPEN"
  }
}
```

### Update Incident

```json
{
  "httpMethod": "PATCH",
  "path": "/incidents/example-incident-id",
  "pathParameters": {
    "incidentId": "example-incident-id"
  },
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"status\":\"investigating\"}"
}
```

### CloudWatch Alarm-to-Incident

This is a CloudWatch-style alarm event manually passed to Lambda. Real CloudWatch alarms are not deployed yet.

```json
{
  "detail-type": "CloudWatch Alarm State Change",
  "source": "aws.cloudwatch",
  "account": "123456789012",
  "region": "us-east-1",
  "time": "2026-06-20T14:25:30Z",
  "detail": {
    "alarmName": "checkout-api-high-5xx",
    "configuration": {
      "description": "Checkout API 5xx error rate exceeded the production threshold."
    },
    "state": {
      "value": "ALARM",
      "reason": "Threshold crossed: 5xx error rate was greater than 5% for 5 minutes.",
      "timestamp": "2026-06-20T14:25:30Z"
    },
    "previousState": {
      "value": "OK",
      "reason": "Previously within threshold.",
      "timestamp": "2026-06-20T14:20:30Z"
    }
  }
}
```

When `INCIDENT_ALERT_TOPIC_ARN` is configured for the Lambda and the incident severity is `HIGH` or `CRITICAL`, the handler should publish a concise SNS alert. Local unit tests mock SNS, so AWS credentials are not needed.

### Manual SNS Publish Test

Before wiring Lambda to SNS, manually validate the topic:

1. Create or select the topic `sirp-incident-alerts-dev`.
2. Confirm the email subscription.
3. Publish a short test message to the topic.
4. Confirm the email arrives from `no-reply@sns.amazonaws.com`.

This proves SNS delivery independently of Lambda code.

### Alarm-to-Incident SNS Test Plan

For manual AWS validation:

1. Configure `sirp-alarm-to-incident-dev` with `INCIDENT_ALERT_TOPIC_ARN`.
2. Confirm the Lambda execution role has `sns:Publish` for the topic ARN.
3. Invoke the Lambda with the CloudWatch-style alarm event above.
4. Confirm a DynamoDB incident is created.
5. Confirm the SNS email arrives for HIGH or CRITICAL severity.
6. Invoke the exact same event again.
7. Confirm the same incident id is returned and no duplicate email is expected.

LOW and MEDIUM incidents should not publish SNS alerts.

### Latest SNS-Enabled Validation Result

The latest manual validation confirmed the SNS-enabled `alarm_to_incident` path in AWS:

- Updated `lambda-package.zip` was uploaded to S3.
- `sirp-alarm-to-incident-dev` was updated from the latest S3 package.
- A CloudWatch-style Lambda test event was run with:
  - `alarmName`: `checkout-api-high-5xx-sns-test`
  - `timestamp`: `2026-06-22T18:30:00Z`
- Lambda returned `statusCode` `201`.
- DynamoDB stored incident `alarm-06aef43378caa053` with `severity` `HIGH`, `status` `OPEN`, and `source` `cloudwatch`.
- SNS email alert was received.

This was not a real CloudWatch alarm trigger. It was still manually tested through a Lambda test event.

### SAM-Deployed SNS Validation Result

The SAM/CloudFormation stack `sirp-dev` was deployed and validated with the SAM-managed alarm-to-incident Lambda.

Validated function configuration for `sirp-alarm-to-incident-sam-dev`:

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
- Created incident `alarm-90eb8d0c5dedab14`
- Incident fields: `severity=HIGH`, `status=OPEN`, `source=cloudwatch`
- SNS email alert was received.

This was still not a real CloudWatch alarm trigger. The event was manually supplied through Lambda testing.

### Real CloudWatch Alarm Trigger Test

After deploying the SAM stack, validate the real alarm path:

1. Invoke `sirp-failure-simulator-sam-dev`.
2. Confirm the invocation fails intentionally.
3. Wait for CloudWatch alarm `sirp-failure-simulator-errors-sam-dev` to evaluate the Lambda `Errors` metric.
4. Confirm the alarm enters `ALARM`.
5. Confirm EventBridge rule `sirp-failure-simulator-alarm-rule-sam-dev` invokes `sirp-alarm-to-incident-sam-dev`.
6. Confirm DynamoDB table `sirp-incidents-sam-dev` contains a new incident.
7. Confirm an SNS email alert is received.

The failure simulator Lambda should not be used for production traffic. It exists only to create a controlled CloudWatch `Errors` metric for validation.

### Real CloudWatch Alarm Validation Result

The fully automated flow was successfully validated:

```text
sirp-failure-simulator-sam-dev intentionally failed
  -> CloudWatch Lambda Errors metric was recorded
  -> CloudWatch alarm sirp-failure-simulator-errors-sam-dev entered ALARM
  -> EventBridge rule sirp-failure-simulator-alarm-rule-sam-dev matched the alarm state change
  -> sirp-alarm-to-incident-sam-dev was invoked automatically
  -> DynamoDB table sirp-incidents-sam-dev stored a new incident
  -> SNS email alert was received
```

Failure simulator invoke returned:

- `StatusCode`: `200`
- `FunctionError`: `Unhandled`
- `RuntimeError: Intentional failure generated for SIRP CloudWatch alarm test.`

DynamoDB confirmed:

- `id`: `alarm-8a107dc637b96a30`
- `alarmName`: `sirp-failure-simulator-errors-sam-dev`
- `severity`: `HIGH`
- `status`: `OPEN`
- `source`: `cloudwatch`
- `alarmState`: `ALARM`
- `createdAt`: `2026-06-23T16:47:27Z`

The SNS email alert arrived after a slight delay, which is expected because CloudWatch alarm evaluation and EventBridge delivery are asynchronous.

### Testing SNS Without AWS

Unit tests mock the SNS client and set `INCIDENT_ALERT_TOPIC_ARN` only inside the test case. This verifies that the code attempts to publish for HIGH/CRITICAL incidents without using AWS credentials.

### Escalation

```json
{
  "cutoffTimestamp": "2027-01-01T00:00:00Z"
}
```

## Current Validation Checklist

Run these commands before committing changes:

```bash
python -m unittest discover -s tests
python -m compileall src tests
python -m json.tool events/alarm_event.json
python -m json.tool events/create_incident.json
python -m json.tool events/update_incident.json
```
