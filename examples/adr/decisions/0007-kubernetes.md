---
status: accepted
date: 2025-09-01
supersedes: ADR-0004
---
# ADR-0007: Kubernetes, one namespace per environment

## Context
Seven services, traffic peaks on sale days, and hand-added VMs took a day to bring up.

## Decision
Larkspur runs on a managed Kubernetes cluster with one namespace per environment. Each service is a Helm chart;
releases go through Argo CD. Horizontal pod autoscaling on CPU and request rate.

## Consequences
Sale-day scaling is automatic. The team must learn Kubernetes operations.
