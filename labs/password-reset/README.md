# Password Reset Lab

This lab covers requesting and confirming password resets.

## What Runs Locally

- `POST /auth/password-reset/request`
- `POST /auth/password-reset/confirm`
- Signed expiring reset tokens
- Local token preview through `AUTH_EXPOSE_RESET_TOKEN=true`
- Generic request response for missing and existing accounts
- Password update through the service layer

## What Is Simplified

- No email provider integration.
- No email template rendering.
- No request cooldown in the route handler.
- No user notification after password changes.
- Local token preview is enabled by default for a runnable demo.

## What Breaks In Production

- Reset tokens must not be returned in API responses.
- Reset requests need per-email and per-IP cooldowns.
- Stateless reset tokens cannot be revoked one by one.
- Password changes may need to invalidate active sessions.
- Account recovery can become an abuse path without monitoring.

## Hardening Steps

- Set `AUTH_EXPOSE_RESET_TOKEN=false`.
- Send reset links through a monitored transactional email provider.
- Add cooldowns using the [rate-limited auth](../rate-limited-auth/README.md) lab.
- Use stateful auth action tokens when reset links must be single-use.
- Add post-reset notifications.
- Decide whether password changes should bump a token version or revoke sessions.

## Tests Included

- `tests/test_auth_flow.py::test_password_reset_changes_password`
- `tests/test_auth_flow.py::test_password_reset_request_does_not_error_for_unknown_email`
- `tests/test_auth_flow.py::test_password_reset_rejects_invalid_token`
- `tests/test_auth_flow.py::test_password_reset_rejects_new_password_over_bcrypt_byte_limit`
- `tests/test_auth_flow.py::test_password_reset_rejects_expired_token`
- `tests/test_auth_action_tokens.py`

## Provider Handoff Options

Use hosted auth when account recovery must be tied to MFA, passkeys, risk scoring, support workflows, enterprise identity, or an admin console.
