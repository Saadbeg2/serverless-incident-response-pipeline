# Cost Control

This project is designed for low-cost AWS learning and portfolio use.

## Services Intentionally Avoided

The project avoids infrastructure that can create steady or unexpected costs, including:

- EC2
- RDS
- ECS
- ALB
- NAT Gateway
- Transit Gateway

## Cost-Control Principles

- Prefer serverless services with free tier or usage-based pricing.
- Keep Lambda memory and timeout settings modest.
- Use DynamoDB carefully and start with small test data.
- Avoid always-on compute.
- Keep deployments easy to tear down.

## Current Status

The current repository contains only scaffolding and documentation. The placeholder template does not create paid AWS resources.
