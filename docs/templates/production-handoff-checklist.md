# Auth Production Handoff Checklist

Use this checklist when adapting the starter for a real product.

## Environment

- [ ] `AUTH_ENV=production` is set in the production environment.
- [ ] `AUTH_SECRET_KEY` is long, random, and stored outside source control.
- [ ] `AUTH_TOKEN_ALGORITHM` is explicitly set.
- [ ] Token TTLs are positive and match the product session policy.
- [ ] Local token preview settings are disabled:
  - [ ] `AUTH_EXPOSE_RESET_TOKEN=false`
  - [ ] `AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=false`

## Database

- [ ] The team has decided whether the default SQLite route path is still acceptable.
- [ ] If SQLite routes are used, `AUTH_ALLOW_SQLITE_IN_PRODUCTION=true` is documented as an explicit acknowledgement.
- [ ] Managed database ownership is defined if moving beyond SQLite.
- [ ] Schema migration ownership is defined.
- [ ] Backups and restore checks are documented.

## Auth Flows

- [ ] Registration duplicate-email behavior is chosen:
  - [ ] explicit
  - [ ] generic anti-enumeration
- [ ] Email verification access policy is chosen.
- [ ] Password reset response does not reveal whether an account exists.
- [ ] Reset and verification token mode is chosen:
  - [ ] stateless JWT
  - [ ] stateful single-use tokens
- [ ] Password reset invalidates old access tokens.
- [ ] Bcrypt 72-byte limit or Argon2id migration path is documented.

## Abuse Protection

- [ ] Login throttling is implemented.
- [ ] Registration throttling is implemented.
- [ ] Password reset request throttling is implemented.
- [ ] Email verification resend throttling is implemented.
- [ ] Proxy and client IP trust boundary is documented.
- [ ] Audit event retention policy is documented.
- [ ] Alerting exists for spikes in failed login or reset traffic.

## Email Delivery

- [ ] Verification email provider is chosen.
- [ ] Password reset email provider is chosen.
- [ ] Sending domain is configured.
- [ ] Bounce and delivery monitoring are owned.
- [ ] Email templates do not expose internal implementation details.

## Operations

- [ ] Dependency scanning is enabled.
- [ ] Security reporting path is documented.
- [ ] Incident owner is assigned.
- [ ] Support recovery workflow is documented.
- [ ] Hosted auth migration criteria are documented.

## Provider Decision

- [ ] Local auth responsibilities are understood.
- [ ] Hosted auth requirements have been reviewed.
- [ ] Provider comparison uses evidence labels, not paid placement.
- [ ] Any commercial links include nearby disclosure.
