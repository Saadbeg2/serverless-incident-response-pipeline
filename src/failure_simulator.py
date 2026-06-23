"""Intentional failure Lambda for CloudWatch alarm validation."""


def handler(event, context):
    print("Intentional failure generated for SIRP CloudWatch alarm test.")
    raise RuntimeError("Intentional failure generated for SIRP CloudWatch alarm test.")
