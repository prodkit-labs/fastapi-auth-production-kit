# Data Model

This page explains the local SQLite schema and the optional SQLAlchemy/Postgres track.

The default FastAPI routes use SQLite through `AUTH_DATABASE_PATH`. The SQLAlchemy track is a production persistence pattern and is not wired into the default routes yet.

## `users`

The local `users` table stores account identity, password hash, email verification state, and token invalidation state.

| Column | Purpose |
|---|---|
| `id` | Local integer user id |
| `email` | Lowercased unique email address |
| `password_hash` | Password hash from the configured password hashing path |
| `verified_at` | Timestamp set when email verification succeeds |
| `token_version` | Server-side version used to reject access tokens issued before password reset |
| `created_at` | Account creation timestamp |

Notes:

- email addresses are normalized to lowercase before storage
- password hashes are stored, never raw passwords
- password reset increments `token_version`
- `/me` rejects access tokens whose `token_version` no longer matches the user row

## `auth_action_tokens`

The `auth_action_tokens` table supports optional stateful reset and verification links.

| Column | Purpose |
|---|---|
| `id` | Local token row id |
| `user_id` | User who owns the action token |
| `token_hash` | Hash of the raw action token |
| `purpose` | `email_verification` or `password_reset` |
| `expires_at` | Expiry timestamp |
| `used_at` | Timestamp set when the token is consumed |
| `created_at` | Token creation timestamp |
| `request_ip_hash` | Optional hashed request IP metadata |
| `user_agent_hash` | Optional hashed user-agent metadata |

The raw token is returned once. The table stores only the token hash.

When `AUTH_ACTION_TOKEN_MODE=stateful`, reset and verification confirmation consume tokens through an atomic update that requires:

- matching token hash
- matching purpose
- `used_at IS NULL`
- `expires_at` later than the current time

## `auth_events`

The `auth_events` table supports local abuse-protection experiments.

| Column | Purpose |
|---|---|
| `id` | Local event row id |
| `event_type` | Event category |
| `email_hash` | HMAC hash of an email identifier |
| `ip_hash` | HMAC hash of an IP identifier |
| `occurred_at` | Event timestamp |
| `metadata` | JSON text for small event details |

Current event types:

- `login_failed`
- `password_reset_request`
- `email_verification_request`
- `registration_attempt`

Hashes use `AUTH_EVENT_HASH_PEPPER`. Do not treat this local table as a distributed production limiter; use shared infrastructure when running multiple app instances.

## SQLAlchemy Track

The SQLAlchemy track exports:

- `AuthBase`
- `UserModel`
- `database_url_from_settings`
- `create_auth_engine`
- `create_session_factory`
- `initialize_auth_schema`
- `auth_session`

`UserModel` mirrors the basic account shape:

| Field | Purpose |
|---|---|
| `id` | Primary key |
| `email` | Unique indexed email address |
| `password_hash` | Password hash |
| `verified_at` | Email verification timestamp |
| `created_at` | Account creation timestamp |

The track intentionally uses `create_all` only for tests, demos, and first-run experiments. Use [migration path](../production/migrations.md) before production schema changes.
