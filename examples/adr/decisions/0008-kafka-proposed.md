---
status: proposed
date: 2025-10-06
---
# ADR-0008: Kafka as the event bus

## Context
Fulfilment polls the order service every 30 s for paid orders.

## Decision (proposed)
Publish order events to Kafka; fulfilment and analytics consume them.

## Consequences
Removes polling. Adds a cluster to operate. Not yet decided.
