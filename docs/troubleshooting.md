# Troubleshooting

This document will collect common issues and fixes as the project grows.

## Lambda Timeout

During manual validation, the initial Lambda timeout was 3 seconds. Some invocations failed with `Sandbox.Timeout` errors.

Fix:

- Set Lambda memory to 256 MB.
- Set Lambda timeout to 10 seconds.

This gave the functions enough room for cold starts and DynamoDB calls during validation.

## Wrong Alarm Event Shape

Early `alarm_to_incident` tests used the wrong event shape. The handler could not find the expected alarm fields and created `unknown-alarm` records.

Fix:

- Use the CloudWatch Alarm State Change style event from `events/alarm_event.json`.
- Remember that real CloudWatch alarms are not deployed yet. These are manually supplied Lambda test events.

## Missing S3 Tagging and Encryption Permissions

S3 bucket creation initially failed because the `SIRP` IAM user was missing permissions for bucket default encryption and bucket tagging.

Fix:

- Add the required S3 permissions for encryption configuration and tagging during the manual build.
- Keep resource creation scoped to the project naming pattern where possible.

## IAM Console Navigation Errors

The AWS console needed `ListRoles` and `ListPolicies` permissions for IAM navigation. Without them, console pages could show access errors even when scoped resource creation permissions were present.

Fix:

- Add read/list permissions needed for console navigation.
- Keep create/update/delete permissions scoped as tightly as practical.

## S3 Object Tag Warning

An S3 object tag warning appeared during upload.

Impact:

- The warning did not block the Lambda artifact upload.
- The project was still able to create Lambda functions from the uploaded zip file.

## Missing SNS Subscription Console Permission

The SNS console may show errors if the IAM user is missing `sns:GetSubscriptionAttributes`.

Fix:

- Add read permissions needed to inspect SNS subscriptions in the console.
- Keep publish and management permissions scoped to the project topic where possible.

## Missing SNS Console Navigation Permissions

The SNS console may require list/read permissions to navigate topics and subscriptions.

Fix:

- Add the minimum SNS list/read permissions needed for console navigation.
- Avoid broad write permissions unless they are required for the manual validation task.

## Missing Lambda SNS Publish Permission

If `alarm_to_incident` creates the incident but no alert is delivered, the Lambda role may be missing `sns:Publish`.

Fix:

- Add `sns:Publish` to the Lambda execution role.
- Scope the permission to `arn:aws:sns:us-east-1:107570341596:sirp-incident-alerts-dev`.

## Missing Alert Topic Environment Variable

SNS publishing is controlled by `INCIDENT_ALERT_TOPIC_ARN`. If this variable is not set, the Lambda intentionally skips SNS publishing and continues normally.

Fix:

- Set `INCIDENT_ALERT_TOPIC_ARN` on `sirp-alarm-to-incident-dev`.
- Keep `INCIDENTS_TABLE_NAME` set at the same time.

Validation note:

- The SNS-enabled alarm-to-incident path was manually validated after the updated package was uploaded to S3 and `sirp-alarm-to-incident-dev` was updated from that package.
- The successful test used a CloudWatch-style Lambda test event with `alarmName` `checkout-api-high-5xx-sns-test` and timestamp `2026-06-22T18:30:00Z`.
- The Lambda returned `statusCode` `201`, DynamoDB stored incident `alarm-06aef43378caa053`, and an SNS email was received.
- This does not mean a real CloudWatch alarm trigger is connected yet.

## Unconfirmed Email Subscription

SNS will not deliver email alerts until the subscription is confirmed.

Fix:

- Check the subscription inbox.
- Confirm the SNS subscription link.
- Publish a manual SNS test message before expecting Lambda-generated alerts.

## Future Topics

- Lambda invocation errors
- IAM permission errors
- API Gateway response errors
- DynamoDB read and write issues
- SNS and EventBridge delivery issues
