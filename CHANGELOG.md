# Changelog

## Unreleased

## v0.2.1 - Runtime Audit Fixes

- Fixed bcrypt login truncation by enforcing the 72-byte bcrypt input limit in login request parsing and password verification.
- Aligned package and API version metadata with `v0.2.1`.
- Clarified that `AUTH_DATABASE_URL` is for the optional SQLAlchemy/Postgres track and is not wired into default routes yet.
- Fixed settings construction through field names and malformed access-token subjects returning 401.

## v0.2.0 - Auth Production Hardening

Second release of FastAPI Auth Production Kit.

This release turns the runnable auth starter into a stronger production handoff kit with safety guards, clearer security boundaries, password hashing guidance, abuse-protection helpers, provider comparison evidence labels, and reusable auth workflow labs.

Included:

- Added reusable auth production lab structure.
- Expanded provider comparison categories and evidence labels.
- Added optional anti-enumeration registration response mode.
- Added rate-limited auth lab with local event store and cooldown helpers.
- Added stateful auth action token store for single-use reset and verification hardening.
- Added optional Argon2id password hashing track and password hashing guide.
- Added repository security policy and LF formatting rules.
- Added `AUTH_ENV=production` guard for unsafe local defaults.
- Added bcrypt 72-byte password input enforcement.
- Added token strategy and provider evidence notes.
- Added optional SQLAlchemy/Postgres track with model, session pattern, production docs, and local SQLite-backed tests.

Validation:

- `ruff check .`
- `pytest`

## v0.1.0 - Initial runnable auth kit

First runnable release of FastAPI Auth Production Kit.

Included:

- FastAPI app factory and local API routes.
- SQLite user store with a lightweight schema setup path.
- Email/password registration and login.
- JWT access tokens.
- Protected `/me` route.
- Email verification with signed expiring tokens.
- Password reset with signed expiring tokens.
- Local-development token preview settings for verification and reset flows.
- Optional verified-email login policy.
- Environment-driven settings through `.env`.
- Pytest coverage for register, login, verification, reset, duplicate users, and protected routes.
- GitHub Actions test workflow.
- Production guides for security, deployment, provider comparison, and disclosure.

Validation:

- `ruff check .`
- `pytest`
