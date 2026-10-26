---
status: superseded
date: 2025-01-20
superseded-by: ADR-0006
---
# ADR-0002: REST + JSON between all services

## Context
Three services, one small team. Everyone knows HTTP and JSON.

## Decision
All services talk to each other over REST with JSON bodies. Internal service calls use REST + JSON, the same as the
public API. OpenAPI documents every endpoint.

## Consequences
Simple to debug with curl. Payloads are verbose; no schema is enforced at runtime.
