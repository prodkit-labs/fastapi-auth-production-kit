# Security Checklist

Use this checklist before adapting the kit for a real product.

## Required

- Set a long random `AUTH_SECRET_KEY` outside source control.
- Use HTTPS in every non-local environment.
- Store production data in a managed database with backups.
- Add rate limits to login and register routes.
- Add structured audit events for login attempts and account changes.
- Set an account access policy for unverified users.
- Set `AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=false` outside local development.
- Send verification links through an email service you can monitor.
- Add resend limits and abuse monitoring for email verification requests.
- Add password reset flows only with signed, expiring tokens.
- Set `AUTH_EXPOSE_RESET_TOKEN=false` outside local development.
- Send reset links through an email service you can monitor.
- Use a generic password reset response so requests do not reveal account existence.
- Add resend limits and abuse monitoring for password reset requests.
- Review session lifetime and refresh-token needs for your product.
- Add monitoring for spikes in failed login attempts.
- Run dependency scanning in CI.

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
