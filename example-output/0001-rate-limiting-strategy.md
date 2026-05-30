---
id: "0001"
title: "Rate Limiting Strategy for Public API"
status: accepted
date: 2026-05-29
deciders: Jaspreet Singh
issue: "https://github.com/tiangolo/fastapi/issues/1234"
validated: false
repo: tiangolo/fastapi
language: Python
framework: FastAPI
time_taken_seconds: 287
tokens_input: 74000
tokens_output: 9800
files_explored: 9
approach_recommended: C
approach_chosen: C
estimated_human_hours: 3
---

## Context

The public API currently has no rate limiting. Under load testing we observed that a single
misbehaving client can exhaust the connection pool for all other users. The API serves both
authenticated users (JWT tokens) and anonymous public endpoints. Any solution must work with
the existing FastAPI middleware stack and not require changes to individual route handlers.

Prior art in the codebase: `app/middleware/auth.py` uses a middleware pattern that runs
before every request — the same hook point any rate limiter would use. The existing Redis
instance (`app/core/cache.py`) is already used for session caching and is available for
a sliding-window counter.

## Decision

We will use **Pragmatic: Redis sliding-window middleware** — a single middleware class that
counts requests per client (by IP for anonymous, by user ID for authenticated) using the
existing Redis instance, with configurable per-route limits via a route decorator.

## Approaches Considered

### Option A — Minimal: Reverse-proxy rate limiting (Nginx / Cloudflare)
Add rate limiting at the infrastructure layer — no application code changes required.
**Why not chosen:** The team doesn't own the Nginx config (managed by platform team), and
per-user limits (authenticated vs anonymous) require application-level context we can't
pass to the proxy easily.

### Option B — Clean: Dedicated rate-limit service with token bucket algorithm
A standalone microservice that all API instances call before processing a request. Supports
distributed rate limiting across multiple API pods with perfect accuracy.
**Why not chosen:** Adds a synchronous network hop to every request, introduces a new
service to operate, and is over-engineered for current traffic volume (< 500 RPS).

### Option C — Pragmatic: Redis sliding-window middleware (chosen)
A FastAPI middleware class backed by the existing Redis instance. Uses a sliding window
counter (not a fixed window) to avoid boundary spikes. Per-route limits are set via a
`@rate_limit(requests=100, window=60)` decorator — no changes to existing routes unless
a custom limit is needed. The default limit (200 req/min per IP) applies globally.

**Why chosen:** Uses existing Redis infrastructure (no new dependencies), integrates with
the existing middleware pattern, supports per-user limits, and can be shipped in one PR.
Clean architecture can be adopted if we move to multi-region later.

## Trade-Off Table

| Criterion       | Minimal (Proxy) | Clean (Service) | Pragmatic (Redis MW) |
|-----------------|-----------------|-----------------|----------------------|
| Ship speed      | High            | Low             | High                 |
| Maintainability | High            | Medium          | High                 |
| Risk            | Low             | High            | Low                  |
| Reversibility   | High            | Low             | High                 |
| Per-user limits | No              | Yes             | Yes                  |

## Consequences

**Positive:**
- No new infrastructure — uses the Redis instance already in prod
- Rate limit config is colocated with the route definition (readable, reviewable)
- Anonymous and authenticated clients get different limits automatically
- Middleware can be disabled per-environment via feature flag

**Negative / watch for:**
- Redis becomes a hard dependency — if Redis is down, the rate limiter must fail open
  (allow requests) or fail closed (block all). Chose fail open; document this.
- Sliding window requires two Redis commands per request — adds ~1ms latency. Acceptable
  at current traffic; revisit if RPS exceeds 2k.
- Does not protect against distributed attacks across many IPs — that requires CDN-level
  blocking which remains a future concern.

## Key Files

- `app/middleware/auth.py` — existing middleware pattern this follows
- `app/core/cache.py` — Redis client to reuse
- `app/middleware/rate_limit.py` — new file created by this decision
- `app/core/config.py` — where default rate limit values are added
- `tests/middleware/test_rate_limit.py` — new test file

## Related ADRs

- None (first ADR in this project)
