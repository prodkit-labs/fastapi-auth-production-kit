# Deployment

The local app uses SQLite because it keeps the first run simple. Production deployments should use a managed database and environment-managed secrets.

## Minimum Environment

```text
AUTH_DATABASE_PATH=/data/prodkit-auth.sqlite3
AUTH_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
AUTH_SECRET_KEY=<long-random-secret>
AUTH_ACCESS_TOKEN_MINUTES=30
```

## Production Notes

- Put the app behind HTTPS.
- Keep the secret key in the host's secret manager.
- Use a persistent volume or managed database.
- Run tests before every deploy.
- Add rate limiting at the edge or application layer.
- Record operational decisions in your own runbook.
- Use the [SQLAlchemy and Postgres track](sqlalchemy-postgres.md) when auth data needs a managed database.

## Hosted Platform Fit

Small FastAPI apps commonly start on platforms such as Railway, Render, Fly.io, or a container host. Choose based on database support, secret handling, logs, deploy rollback, and pricing predictability.
