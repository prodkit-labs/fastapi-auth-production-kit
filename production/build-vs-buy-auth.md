# Build Vs Buy Auth

This guide helps teams decide when to keep the local FastAPI auth path, when to harden it, and when to move identity work to a hosted provider.

The default answer is not "always build" or "always buy." The right choice depends on your product risk, team capacity, user model, and compliance needs.

## When Local Auth Is Enough

The local path can be a good fit when:

- the product is an internal tool, prototype, or small application
- users only need email and password auth
- account recovery can be handled by a small team
- there is no immediate need for social login, SAML, SCIM, MFA, passkeys, or organization membership
- the team can own secrets, backups, dependency updates, logs, alerts, and incident response

Use the local path to learn your product's account model before adding provider coupling.

## When Local Auth Becomes Risky

Local auth becomes a larger responsibility when:

- failed login, reset, or verification traffic grows
- the product needs long-lived sessions across multiple devices
- support teams need account recovery tooling
- password reset links must be single-use and auditable
- account existence must be hidden from public flows
- customers expect MFA, device management, organization roles, or audit logs
- compliance or enterprise procurement starts asking about identity controls

At that point, the cost is no longer only implementation time. It includes operations, monitoring, support workflows, and security review.

## When Hosted Auth Is Worth It

Hosted auth can be worth considering when the provider replaces work your team would otherwise have to maintain:

- hosted sign-in and account management UI
- social login
- MFA and passkeys
- organization membership
- SAML/OIDC and enterprise identity
- device and session management
- admin console
- audit logs
- email delivery and account recovery workflows

Provider adoption is not free. Review pricing, data portability, customization limits, outage handling, and the path back to local control before committing.

## Decision Checklist

| Question | Local auth can fit | Hosted auth may fit |
|---|---|---|
| Account model | Individual users | Organizations, teams, tenants |
| Login methods | Email and password | Social login, SSO, MFA, passkeys |
| Session needs | Short-lived API tokens | Device/session dashboard, refresh rotation, logout everywhere |
| Recovery needs | Basic reset email | Support recovery, audit logs, admin tooling |
| Compliance | Low-risk internal use | Enterprise identity or regulated customers |
| Team capacity | Team can own auth operations | Team wants provider-owned identity surface |
| Migration cost | Product is early and simple | Auth complexity already blocks product work |

## Local Hardening Path

If you keep local auth, review these guides before production use:

- [Security checklist](security-checklist.md)
- [Token strategy](token-strategy.md)
- [Password hashing](password-hashing.md)
- [Rate-limited auth](rate-limiting.md)
- [SQLAlchemy and Postgres track](sqlalchemy-postgres.md)
- [Migration path](migrations.md)

Minimum production decisions:

- move secrets to the host secret manager
- disable local token exposure settings
- decide whether reset and verification tokens must be stateful
- add edge and application rate limits
- use a managed database with backups
- define account recovery and support ownership
- document provider migration criteria

## Provider Handoff Path

If you move to hosted auth, document what the provider replaces and what your app still owns.

| Area | Provider may own | Your app still owns |
|---|---|---|
| Authentication | login methods, MFA, sessions | authorization rules, app roles, user data mapping |
| Account recovery | reset links, email flows | support policy, abuse escalation |
| Enterprise identity | SAML/OIDC, directory sync | tenant model, billing entitlements |
| Audit logs | identity events | product-domain events |
| Compliance | provider controls | your app controls and data handling |

Use [provider comparison](provider-comparison.md) as a starting point, not as a ranking.

Provider notes:

- [Clerk migration note](provider-notes/clerk.md)
- [Auth0 migration note](provider-notes/auth0.md)
- [Supabase Auth migration note](provider-notes/supabase-auth.md)
- [Logto migration note](provider-notes/logto.md)
- [Resend email delivery note](provider-notes/resend.md)

## Commercial Links

Do not add affiliate or partner links to this page until there is:

- nearby disclosure
- hands-on provider notes
- a reproducible comparison rubric
- a clear open-source path that does not require a paid provider

See [disclosure policy](disclosure.md).
