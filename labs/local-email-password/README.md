# Local Email/Password Lab

This lab covers the local register, login, and protected-route path.

## What Runs Locally

- `POST /auth/register`
- `POST /auth/login`
- `GET /me`
- SQLite-backed user persistence
- Bcrypt password hashing through `passlib`
- Optional Argon2id helper functions
- JWT access tokens with `sub` and `exp`

## What Is Simplified

- No refresh-token rotation.
- No MFA.
- No account lockout workflow.
- No device or session administration.
- No user-facing account management UI.

## What Breaks In Production

- A default `AUTH_SECRET_KEY` must never be deployed.
- Login and registration need rate limits.
- Long-lived sessions need refresh-token strategy, rotation, and revocation decisions.
- Sensitive products may need generic duplicate-registration responses.
- Bcrypt's 72-byte input limit must remain enforced unless you move passwords to Argon2id.

## Hardening Steps

- Set `AUTH_ENV=production`.
- Set a long random `AUTH_SECRET_KEY`.
- Review [token strategy](../../production/token-strategy.md).
- Review [password hashing](../../production/password-hashing.md).
- Review [anti-enumeration registration](../../production/anti-enumeration.md).
- Add audit events for login, registration, password changes, and account disablement.
- Decide whether unverified users can log in.

## Tests Included

- `tests/test_auth_flow.py::test_register_login_and_read_current_user`
- `tests/test_auth_flow.py::test_duplicate_email_returns_conflict`
- `tests/test_auth_flow.py::test_generic_registration_mode_normalizes_duplicate_email_response`
- `tests/test_auth_flow.py::test_login_rejects_bad_password`
- `tests/test_auth_flow.py::test_protected_route_requires_token`
- `tests/test_password_hashing.py`

## Provider Handoff Options

Use hosted auth when you need social login, MFA, passkeys, organization membership, device/session management, enterprise identity, or admin tooling. See [provider comparison](../../production/provider-comparison.md).
