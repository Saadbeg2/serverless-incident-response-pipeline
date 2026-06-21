"""API Gateway-style response helpers."""

import json

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
}


def success_response(data, status_code=200):
    return {
        "statusCode": status_code,
        "headers": DEFAULT_HEADERS,
        "body": json.dumps(data),
    }


def error_response(message, status_code=400):
    return {
        "statusCode": status_code,
        "headers": DEFAULT_HEADERS,
        "body": json.dumps({"error": message}),
    }
