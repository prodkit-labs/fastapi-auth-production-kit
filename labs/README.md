# Auth Production Labs

These labs turn the starter into a set of reusable auth workflows.

Each lab answers the same production handoff questions:

- What runs locally?
- What is intentionally simplified?
- What breaks in production?
- What hardening steps come next?
- Which tests cover the path?
- When should a hosted provider take over?

## Labs

| Lab | Focus | Local Entry |
|---|---|---|
| [Local email/password](local-email-password/README.md) | Register, login, password hashing, protected route | `/auth/register`, `/auth/login`, `/me` |
| [Email verification](email-verification/README.md) | Verification request and confirm flow | `/auth/email-verification/request`, `/auth/email-verification/confirm` |
| [Password reset](password-reset/README.md) | Reset request and confirm flow | `/auth/password-reset/request`, `/auth/password-reset/confirm` |
| [SQLAlchemy/Postgres](sqlalchemy-postgres/README.md) | Production persistence track | `prodkit_auth.sqlalchemy_track` |
| [Rate-limited auth](rate-limited-auth/README.md) | Local abuse-protection helpers | `record_auth_event`, `too_many_auth_events` |

## How To Use These Labs

Start with the local path that matches the feature you are shipping. Run the tests listed in that lab, then read the hardening steps before adapting it for a real product.

Use [provider comparison](../production/provider-comparison.md) when the product needs hosted UI, social login, MFA, enterprise identity, organization membership, device/session management, admin tooling, or compliance-heavy audit trails.
