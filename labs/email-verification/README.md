# Email Verification Lab

This lab covers requesting and confirming email verification.

## What Runs Locally

- `POST /auth/email-verification/request`
- `POST /auth/email-verification/confirm`
- Signed expiring verification tokens
- Local token preview through `AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=true`
- Verified-user state stored in SQLite

## What Is Simplified

- No email provider integration.
- No email template rendering.
- No resend policy in the route handler.
- No audit trail attached to verification requests.
- Local token preview is enabled by default for a runnable demo.

## What Breaks In Production

- Verification tokens must not be returned in API responses.
- Delivery failures, bounces, and abuse need monitoring.
- Repeated verification requests need cooldowns.
- Stateless verification tokens cannot be revoked one by one.
- Verification links need HTTPS and safe redirect handling.

## Hardening Steps

- Set `AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=false`.
- Send links through a monitored transactional email provider.
- Add resend limits using the [rate-limited auth](../rate-limited-auth/README.md) lab.
- Use stateful auth action tokens when verification links must be single-use.
- Add audit events for request, send, confirm, and failure states.

## Tests Included

- `tests/test_auth_flow.py::test_email_verification_marks_user_verified`
- `tests/test_auth_flow.py::test_verified_email_can_be_required_for_login`
- `tests/test_auth_flow.py::test_email_verification_request_does_not_error_for_unknown_or_verified_email`
- `tests/test_auth_flow.py::test_email_verification_rejects_invalid_and_wrong_purpose_tokens`
- `tests/test_auth_flow.py::test_email_verification_rejects_expired_token`
- `tests/test_auth_action_tokens.py`

## Provider Handoff Options

Use hosted auth when verification must be part of a broader identity system with MFA, social login, organization membership, admin tooling, or device/session management.
