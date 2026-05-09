# Deployment

The local app uses SQLite because it keeps the first run simple. Production deployments should use a managed database and environment-managed secrets.

## Minimum Environment

```text
# Used by the default SQLite app routes:
AUTH_DATABASE_PATH=/data/prodkit-auth.sqlite3
AUTH_ALLOW_SQLITE_IN_PRODUCTION=true

# Used by the optional SQLAlchemy/Postgres track, not by the default app routes yet:
AUTH_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE

AUTH_SECRET_KEY=<long-random-secret>
AUTH_ACCESS_TOKEN_MINUTES=30
AUTH_PASSWORD_RESET_TOKEN_MINUTES=15
AUTH_EMAIL_VERIFICATION_TOKEN_MINUTES=1440
```

## Production Notes

- Put the app behind HTTPS.
- Keep the secret key in the host's secret manager.
- Use a persistent volume or managed database.
- The default FastAPI routes use `AUTH_DATABASE_PATH`.
- Production startup requires `AUTH_ALLOW_SQLITE_IN_PRODUCTION=true` before running the default SQLite route path. This flag is an explicit acknowledgement for the current SQLite route path, not a recommendation to use SQLite for production auth data.
- `AUTH_DATABASE_URL` belongs to the optional SQLAlchemy/Postgres track until the default routes add a database backend switch.
- Do not rely on automatic table creation for production auth data; use the [migration path](migrations.md) before changing live tables.
- Run tests before every deploy.
- Add rate limiting at the edge or application layer.
- Record operational decisions in your own runbook.
- Use the [SQLAlchemy and Postgres track](sqlalchemy-postgres.md) when auth data needs a managed database.

## Hosted Platform Fit

Small FastAPI apps commonly start on platforms such as Railway, Render, Fly.io, or a container host. Choose based on database support, secret handling, logs, deploy rollback, and pricing predictability.
