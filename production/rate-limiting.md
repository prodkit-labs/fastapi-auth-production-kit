# Rate-Limited Auth Lab

This lab adds a local auth event store for abuse-protection experiments. It is not a replacement for edge rate limiting or a production Redis-backed limiter, but it gives you a runnable model for the decisions you need to make.

## Event Types

```text
login_failed
password_reset_request
email_verification_request
```

## Local Event Store

The `auth_events` table stores:

- `event_type`
- `email_hash`
- `ip_hash`
- `occurred_at`
- `metadata`

Email and IP values are hashed before storage. Keep raw request identifiers out of logs and database tables unless your product has a clear retention policy.

## Helpers

```python
from prodkit_auth.service import (
    is_auth_event_rate_limited,
    record_auth_event,
)

record_auth_event(
    connection,
    event_type="login_failed",
    email="dev@example.com",
    ip_address="203.0.113.10",
)

blocked = is_auth_event_rate_limited(
    connection,
    event_type="login_failed",
    email="dev@example.com",
    limit=5,
    window_seconds=300,
)
```

## Suggested Local Policies

| Flow | Local policy example | Production handoff |
|---|---|---|
| Failed login | 5 attempts per email per 5 minutes | Add IP/device signals, alerting, and credential stuffing detection |
| Password reset request | 1 request per email or IP per minute | Add email delivery telemetry and abuse monitoring |
| Email verification resend | 1 request per email per minute | Add resend backoff and support-safe recovery path |

## Production Handoff

For production systems:

- enforce limits at the edge and application layer
- use Redis or a managed rate-limit service for distributed app instances
- separate user-facing messages from internal reasons
- log structured audit events
- monitor spikes in failed login and reset traffic
- define retention for hashed IP and user-agent metadata
