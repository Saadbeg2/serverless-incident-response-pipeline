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

Phase 1 uses `src/incident_store.py` as a small storage abstraction backed by an in-memory dictionary.

This lets the Lambda handlers be tested locally without AWS credentials, DynamoDB tables, or deployment steps. The store supports creating, reading, listing, updating, and finding stale open incidents.

The in-memory store resets when the Python process exits. Unit tests also clear it between test cases so each test starts from a known state.

## Future DynamoDB Integration

DynamoDB integration will come in a later phase. The current store module includes TODO comments showing where DynamoDB `PutItem`, `GetItem`, `UpdateItem`, and query or scan logic will be added.
