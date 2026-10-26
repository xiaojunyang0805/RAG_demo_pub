---
status: accepted
date: 2025-01-14
---
# ADR-0001: PostgreSQL as the system of record

## Context
Orders, reservations and payments must be consistent: an order is paid exactly once and stock is reserved exactly
once. We need transactions across these tables.

## Decision
We use PostgreSQL 16 as the single system of record. Each service owns its schema; no service reads another
service's tables.

## Consequences
Cross-service reads go through APIs. Reporting uses a nightly replica.
