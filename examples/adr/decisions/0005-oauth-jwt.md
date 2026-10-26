---
status: accepted
date: 2025-06-02
supersedes: ADR-0003
---
# ADR-0005: OAuth 2.0 with short-lived JWT access tokens

## Context
The mobile app and two partner integrations cannot use browser cookies. Session lookups in Redis became the
largest share of request latency at peak.

## Decision
Clients authenticate with OAuth 2.0 (authorization code with PKCE for apps, client credentials for partners). The
identity provider issues JWT access tokens valid for 10 minutes; services verify the signature locally. Refresh
tokens live 14 days.

## Consequences
No session store on the request path. Revocation takes up to 10 minutes.
