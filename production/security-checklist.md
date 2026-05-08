# Security Checklist

Use this checklist before adapting the kit for a real product.

## Required

- Set a long random `AUTH_SECRET_KEY` outside source control.
- Use HTTPS in every non-local environment.
- Store production data in a managed database with backups.
- Add rate limits to login and register routes.
- Add structured audit events for login attempts and account changes.
- Add password reset flows only with signed, expiring tokens.
- Review session lifetime and refresh-token needs for your product.
- Add monitoring for spikes in failed login attempts.
- Run dependency scanning in CI.

## Strongly Recommended

- Add email verification before granting full account access.
- Add multi-factor authentication for privileged users.
- Add admin-side account disable and token revocation workflows.
- Keep auth logic behind a small service boundary so it can be replaced by a provider later.

## Out Of Scope For This Starter

- Social login
- SAML
- Enterprise identity federation
- Organization membership and RBAC
- Compliance certification
