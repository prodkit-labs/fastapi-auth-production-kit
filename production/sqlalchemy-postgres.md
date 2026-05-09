# SQLAlchemy And Postgres Track

The default app keeps a direct SQLite path so the first run is small and easy to inspect. Use this track when you are ready to move auth data into a production database.

This track is not wired into the default FastAPI routes yet. The default routes use `AUTH_DATABASE_PATH`; `AUTH_DATABASE_URL` is consumed by this SQLAlchemy/Postgres track and should be treated as an optional production path until a backend switch is added.

## Install

```bash
python -m pip install -e '.[postgres]'
```

For local tests and development, `.[dev]` also installs SQLAlchemy.

## Environment

SQLite through SQLAlchemy:

```text
AUTH_DATABASE_URL=sqlite+pysqlite:///./prodkit-auth.sqlite3
```

Managed Postgres:

```text
AUTH_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

Keep the database URL in your host's secret manager. Do not commit production credentials.

## Session Pattern

```python
from prodkit_auth.config import get_settings
from prodkit_auth.sqlalchemy_track import (
    auth_session,
    create_auth_engine,
    create_session_factory,
    database_url_from_settings,
    initialize_auth_schema,
)

settings = get_settings()
database_url = database_url_from_settings(
    database_url=settings.database_url,
    sqlite_path=settings.database_path,
)
engine = create_auth_engine(database_url)
initialize_auth_schema(engine)
SessionLocal = create_session_factory(engine)

with auth_session(SessionLocal) as session:
    ...
```

## Migration Notes

`initialize_auth_schema()` is intentionally small and useful for a first local run. For production, move schema changes into a migration tool such as Alembic before you change live tables.

Recommended migration order:

- Create the `users` table from `UserModel`.
- Add unique index coverage for `email`.
- Backfill `verified_at` as nullable.
- Add operational backups before importing users.
- Run migrations in staging before production.

## Managed Postgres Checklist

- Use TLS-capable managed Postgres.
- Store `AUTH_DATABASE_URL` as a secret.
- Rotate database credentials outside source control.
- Enable backups and point-in-time recovery when available.
- Monitor connection count, slow queries, storage, and failed logins.
- Keep tests runnable without external services by using SQLite in CI.
