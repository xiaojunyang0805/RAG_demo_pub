---
status: superseded
date: 2025-02-03
superseded-by: ADR-0005
---
# ADR-0003: Server-side sessions with cookies

## Context
Users log in on the web shop. We need to know who is calling.

## Decision
Users authenticate with a username and password; the server creates a session stored in Redis and returns a
session cookie. Every request is authenticated by looking up the session cookie in Redis.

## Consequences
Works for the browser. The mobile app has to carry cookies.
