# Rate-Limited Auth Lab

This lab covers local helpers for abuse-protection experiments around auth flows.

## What Runs Locally

- `record_auth_event`
- `count_auth_events`
- `too_many_auth_events`
- Hashed email and IP identifiers
- SQLite-backed `auth_events` storage
- Local tests for failed login and request cooldown patterns

## What Is Simplified

- Helpers are not wired into route middleware by default.
- No distributed rate limiter is included.
- No CAPTCHA or bot-management provider is included.
- No alerting or dashboard is included.
- No production retention policy is included.

## What Breaks In Production

- In-memory or single-node counters do not work across multiple app instances.
- SQLite is not a shared rate-limit store for distributed deployments.
- Attackers can rotate IPs, user agents, and identifiers.
- Auth event retention may carry privacy and compliance requirements.
- Cooldowns need product-specific copy and support paths.

## Hardening Steps

- Decide per-route limits for registration, login, verification request, and password reset request.
- Store counters in infrastructure that all app instances share.
- Hash identifiers before storage.
- Add structured audit events for account-sensitive changes.
- Monitor spikes in failed login, reset, and verification requests.
- Review [rate-limited auth](../../production/rate-limiting.md).

## Tests Included

- `tests/test_rate_limited_auth.py`

## Provider Handoff Options

Use hosted auth or a dedicated abuse-protection service when you need adaptive risk scoring, bot management, attack dashboards, or managed account-protection workflows.
