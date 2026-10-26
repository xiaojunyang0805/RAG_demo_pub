---
status: accepted
---
# Larkspur — architecture decisions

*Synthetic example corpus for truthrag: a fictional order service. Every name is invented.*

Larkspur takes orders from the web shop and the mobile app, reserves stock and hands paid orders to fulfilment.
Its architecture decisions are recorded as ADRs in `decisions/`, one file each, in the common Markdown ADR format:
YAML front matter with a `status` (`proposed`, `accepted`, `superseded`, `deprecated`), then context, decision and
consequences. A superseded ADR is kept unchanged and names its successor.

| ADR | Decision | Status |
|---|---|---|
| 0001 | PostgreSQL as the system of record | accepted |
| 0002 | REST + JSON between all services | superseded by 0006 |
| 0003 | Server-side sessions with cookies | superseded by 0005 |
| 0004 | Deploy on VMs with Ansible | superseded by 0007 |
| 0005 | OAuth 2.0 with short-lived JWT access tokens | accepted |
| 0006 | gRPC between internal services; REST stays at the edge | accepted |
| 0007 | Kubernetes, one namespace per environment | accepted |
| 0008 | Kafka as the event bus | proposed |
