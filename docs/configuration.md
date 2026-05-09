# Configuration

This page collects the environment variables used by the local starter and production hardening guides.

The defaults are chosen for local development. Production settings should be explicit and stored outside source control.

| Environment variable | Default | Local use | Production note |
|---|---|---|---|
| `AUTH_ENV` | `local` | Selects local, staging, or production behavior | Set `production` to enable startup safety checks |
| `AUTH_DATABASE_PATH` | `./prodkit-auth.sqlite3` | SQLite file for the default routes | Default routes use this path until a backend switch is added |
| `AUTH_DATABASE_URL` | unset | Optional SQLAlchemy/Postgres track | Not wired into default routes yet |
| `AUTH_ALLOW_SQLITE_IN_PRODUCTION` | `false` | Usually not needed locally | Explicit acknowledgement for the current SQLite route path, not a recommendation |
| `AUTH_SECRET_KEY` | `dev-only-change-me` | Local JWT signing secret | Must be long, random, and stored in a secret manager |
| `AUTH_TOKEN_ALGORITHM` | `HS256` | JWT signing algorithm | Allowed values are `HS256`, `HS384`, and `HS512` |
| `AUTH_ACCESS_TOKEN_MINUTES` | `30` | Access token lifetime | Must be positive; tune to product session policy |
| `AUTH_PASSWORD_RESET_TOKEN_MINUTES` | `15` | Password reset token lifetime | Must be positive; keep short in production |
| `AUTH_EMAIL_VERIFICATION_TOKEN_MINUTES` | `1440` | Email verification token lifetime | Must be positive; tune to email delivery and support policy |
| `AUTH_EXPOSE_RESET_TOKEN` | `true` | Returns reset token in local API response | Set `false` outside local development |
| `AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN` | `true` | Returns verification token in local API response | Set `false` outside local development |
| `AUTH_REQUIRE_VERIFIED_EMAIL_FOR_LOGIN` | `false` | Allows unverified users to log in by default | Decide based on account access policy |
| `AUTH_ACTION_TOKEN_MODE` | `jwt` | Uses stateless local reset and verification tokens | Use `stateful` when reset or verification links must be single-use |
| `AUTH_LOCAL_RATE_LIMITS` | `false` | Enables local route-level throttling demo | Use shared infrastructure for distributed production limits |
| `AUTH_EVENT_HASH_PEPPER` | `dev-only-event-hash-pepper` | HMAC key for local auth event identifiers | Must be long, random, and secret when local rate limits are enabled |
| `AUTH_REGISTRATION_ENUMERATION_MODE` | `explicit` | Duplicate registration returns a clear conflict | Use `generic` when account existence should not be revealed |

## Local Example

```text
AUTH_ENV=local
AUTH_DATABASE_PATH=./prodkit-auth.sqlite3
AUTH_SECRET_KEY=dev-only-change-me
AUTH_EXPOSE_RESET_TOKEN=true
AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=true
AUTH_ACTION_TOKEN_MODE=jwt
AUTH_LOCAL_RATE_LIMITS=false
```

## Production Starting Point

```text
AUTH_ENV=production
AUTH_SECRET_KEY=<long-random-secret>
AUTH_TOKEN_ALGORITHM=HS256
AUTH_ACCESS_TOKEN_MINUTES=30
AUTH_PASSWORD_RESET_TOKEN_MINUTES=15
AUTH_EMAIL_VERIFICATION_TOKEN_MINUTES=1440
AUTH_EXPOSE_RESET_TOKEN=false
AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=false
AUTH_ACTION_TOKEN_MODE=stateful
AUTH_REQUIRE_VERIFIED_EMAIL_FOR_LOGIN=true
AUTH_REGISTRATION_ENUMERATION_MODE=generic
```

If the default SQLite routes are used in production, startup requires:

```text
AUTH_ALLOW_SQLITE_IN_PRODUCTION=true
```

That flag records an explicit acknowledgement of the current route path. It is not a recommendation to use SQLite for production auth data. Review [deployment](../production/deployment.md), [SQLAlchemy and Postgres track](../production/sqlalchemy-postgres.md), and [migration path](../production/migrations.md) before storing production auth data.
