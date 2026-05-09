# Changelog

## v0.4.0 - Build Vs Buy Auth Decision Pack

- Added a build-vs-buy auth decision guide for choosing between local auth,
  local hardening, and hosted identity providers.
- Added a configuration reference for environment-driven settings.
- Added a data model reference for local SQLite tables and the SQLAlchemy track.
- Added a production handoff checklist template.
- Added `MANIFEST.in` so source distributions include production docs, labs,
  templates, and repository governance files.
- Added provider migration notes for Clerk, Auth0, Supabase Auth, Logto, and
  Resend with official-doc source links and no commercial links.

## v0.3.1 - Consistency And Security Semantics Fixes

- Made stateful auth action token consumption an atomic update before returning
  the consumed row.
- Fixed SQLAlchemy/Postgres lab and migration docs to use the actual
  `UserModel` and `AuthBase` API names.
- Added `AUTH_TOKEN_ALGORITHM` as the environment alias for token algorithm
  configuration.
- Clarified that `AUTH_ALLOW_SQLITE_IN_PRODUCTION` is an acknowledgement flag,
  not a recommendation to use SQLite for production auth data.
- Added proxy and IP trust-boundary notes to the rate-limiting guide.

## v0.3.0 - Auth Runtime Hardening

This release hardens runtime auth behavior, dependency maintenance, and
production handoff guidance for teams moving beyond a local auth starter.

Included:

- Added access-token invalidation after password reset through a local
  `token_version` claim.
- Added CI matrix, package build, dependency audit, and Dependabot maintenance
  coverage.
- Added explicit migration guidance for the SQLAlchemy/Postgres production
  track.
- Refreshed README workflow commands for password hashing, stateful action
  tokens, local rate limits, and the SQLAlchemy/Postgres track.
- Documented the bcrypt compatibility policy and configured Dependabot to avoid
  bcrypt 5.x while `passlib[bcrypt]` remains the default bcrypt layer.
- Allowed Argon2id helper installs to use `argon2-cffi` 25.x.

Validation:

- `ruff check .`
- `pytest -q`
- `python -m build`
- `python -m pip_audit --skip-editable`

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
