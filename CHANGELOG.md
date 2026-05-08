# Changelog

## Unreleased

- Added repository security policy and LF formatting rules.
- Added `AUTH_ENV=production` guard for unsafe local defaults.
- Added bcrypt 72-byte password input enforcement.
- Added token strategy and provider evidence notes.
- Added optional SQLAlchemy/Postgres track with model, session pattern, production docs, and local SQLite-backed tests.

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
