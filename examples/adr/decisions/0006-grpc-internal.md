---
status: accepted
date: 2025-07-15
supersedes: ADR-0002
---
# ADR-0006: gRPC between internal services; REST stays at the edge

## Context
Seven services now. A schema change in one REST payload broke two consumers in production.

## Decision
Internal service-to-service calls use gRPC with Protocol Buffers; schemas live in one repository and are checked
for breaking changes in CI. The public API for the web shop, the app and partners stays REST + JSON.

## Consequences
Breaking changes are caught before merge. Debugging needs grpcurl.
