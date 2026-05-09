# SQLAlchemy/Postgres Lab

This lab covers the production persistence track for teams that want to move beyond the local SQLite helper.

## What Runs Locally

- `prodkit_auth.sqlalchemy_track.User`
- `prodkit_auth.sqlalchemy_track.create_engine_from_settings`
- `prodkit_auth.sqlalchemy_track.session_scope`
- SQLAlchemy-backed table creation in tests
- SQLite-compatible local test path

## What Is Simplified

- No migration runner is included.
- No connection pool tuning is included.
- No deployment-specific database provisioning is included.
- No backup or restore automation is included.
- The main FastAPI routes still use the lightweight SQLite path by default.

## What Breaks In Production

- Production schema changes need migrations.
- Database URLs must stay outside source control.
- Connection pooling needs tuning for the host.
- Backups and restore drills need an owner.
- Operational monitoring needs database metrics and slow-query visibility.

## Hardening Steps

- Install the optional extra with `python -m pip install -e '.[postgres]'`.
- Set `AUTH_DATABASE_URL` outside source control.
- Add Alembic or your existing migration system.
- Add backup, restore, and retention rules.
- Review [SQLAlchemy and Postgres track](../../production/sqlalchemy-postgres.md).
- Decide when the route layer should move from the SQLite helper to the SQLAlchemy session pattern.

## Tests Included

- `tests/test_sqlalchemy_track.py`

## Provider Handoff Options

Database providers do not replace auth providers. Use managed Postgres when you want to keep local auth but move persistence to hosted infrastructure. Use hosted auth when identity operations, account lifecycle, or compliance needs exceed what this starter should own.
