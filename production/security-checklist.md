# Security Checklist

Use this checklist before adapting the kit for a real product.

## Required

- Set a long random `AUTH_SECRET_KEY` outside source control.
- Use at least 32 characters for `AUTH_SECRET_KEY`.
- Set `AUTH_ENV=production` and confirm startup rejects unsafe local defaults.
- Keep token TTL settings positive: `AUTH_ACCESS_TOKEN_MINUTES`, `AUTH_PASSWORD_RESET_TOKEN_MINUTES`, and `AUTH_EMAIL_VERIFICATION_TOKEN_MINUTES`.
- Set `AUTH_ALLOW_SQLITE_IN_PRODUCTION=true` only when you intentionally accept the default SQLite route path for a production deployment. This is an acknowledgement flag, not a recommendation to use SQLite for production auth data.
- Use HTTPS in every non-local environment.
- Store production data in a managed database with backups.
- Add rate limits to login and register routes.
- Review [rate-limited auth](rate-limiting.md) before exposing auth endpoints publicly.
- Use `AUTH_LOCAL_RATE_LIMITS=true` only as a local route-level demonstration; use shared infrastructure for distributed deployments.
- Set a long random `AUTH_EVENT_HASH_PEPPER` when local rate-limit events are enabled in production.
- Add structured audit events for login attempts and account changes.
- Review [anti-enumeration registration](anti-enumeration.md) and use `AUTH_REGISTRATION_ENUMERATION_MODE=generic` when duplicate registration responses should not reveal account existence.
- Set an account access policy for unverified users.
- Set `AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=false` outside local development.
- Use `AUTH_ACTION_TOKEN_MODE=stateful` when verification links must be single-use.
- Send verification links through an email service you can monitor.
- Add resend limits and abuse monitoring for email verification requests.
- Add password reset flows only with signed, expiring tokens.
- Set `AUTH_EXPOSE_RESET_TOKEN=false` outside local development.
- Use `AUTH_ACTION_TOKEN_MODE=stateful` when reset links must be single-use.
- Send reset links through an email service you can monitor.
- Use a generic password reset response so requests do not reveal account existence.
- Add resend limits and abuse monitoring for password reset requests.
- Review session lifetime and refresh-token needs for your product.
- Review [token strategy](token-strategy.md) before relying on stateless reset or verification tokens.
- Use stateful auth action tokens when reset or verification links must be single-use.
- Review [password hashing](password-hashing.md), enforce bcrypt's 72-byte input limit, or move new production passwords to the Argon2id track.
- Keep bcrypt pinned below 5 while `passlib[bcrypt]` remains the default bcrypt compatibility layer.
- Add monitoring for spikes in failed login attempts.
- Run dependency scanning in CI.
- Keep Dependabot enabled for Python dependencies and GitHub Actions updates.

## Strongly Recommended

- Add multi-factor authentication for privileged users.
- Add admin-side account disable and token revocation workflows.
- Keep auth logic behind a small service boundary so it can be replaced by a provider later.

## Out Of Scope For This Starter

- Social login
- SAML
- Enterprise identity federation
- Organization membership and RBAC
- Compliance certification
