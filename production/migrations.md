# Migration Path

The default app creates its SQLite schema at startup so the first run stays
small. That path is for local demos, tests, and first-run experiments. Do not
use automatic table creation as your production migration strategy.

Production auth data needs an explicit migration owner, reviewable migration
files, backups, and a staging run before live tables change.

## What `create_all` Is For

`initialize_auth_schema()` in the SQLAlchemy/Postgres track calls SQLAlchemy's
`create_all` helper. It is useful for:

- local SQLAlchemy smoke tests
- short-lived demo databases
- first-run experiments before data exists
- validating the model shape during development

It is not enough for:

- changing live production tables
- reviewing schema changes before deploy
- backfilling existing users
- rolling back failed migrations
- coordinating deploy order across app instances

## Recommended Production Path

Use Alembic or your existing migration system once the auth database contains
real users.

1. Keep the default SQLite routes as the local runnable path until you are ready
   to adopt the SQLAlchemy/Postgres track.
2. Install the optional Postgres dependencies:

   ```bash
   python -m pip install -e '.[postgres]'
   ```

3. Configure `AUTH_DATABASE_URL` in your deployment secret manager.
4. Generate an initial migration from the SQLAlchemy `UserModel`.
5. Review the migration file into source control.
6. Run the migration against a staging database.
7. Run the app test suite against the migrated staging database or an equivalent
   disposable database.
8. Take or verify a production backup.
9. Apply the migration during a planned deploy window.
10. Monitor login, registration, verification, and reset flows after deploy.

## Alembic Adoption Sketch

This repo does not include Alembic in the default app because migration tooling
depends on your deployment process. A typical adoption looks like:

```bash
python -m pip install alembic
alembic init migrations
```

Then point Alembic at the SQLAlchemy metadata:

```python
from prodkit_auth.sqlalchemy_track import AuthBase

target_metadata = AuthBase.metadata
```

Use your environment's secret manager to provide the database URL at migration
time. Do not commit a production `AUTH_DATABASE_URL`.

## First Schema To Capture

The initial SQLAlchemy/Postgres track schema should capture:

- `users.id`
- `users.email` with unique index coverage
- `users.password_hash`
- `users.verified_at`
- `users.token_version`
- `users.created_at`

If you already have users in the default SQLite route path, plan a separate
data import and password-hash compatibility check before switching traffic.

## Switch Readiness Checklist

- Migration files are reviewed.
- Staging migration has run from an empty database and from a copy-like database.
- Backups and restore process have an owner.
- `AUTH_DATABASE_URL` is stored outside source control.
- Connection limits and pool sizing match your host.
- Login, registration, verification, password reset, and `/me` are tested after
  migration.
- Rollback behavior is documented for both schema and app deploys.

## Non-Goals

- This guide does not switch the default route layer to SQLAlchemy.
- This guide does not choose a managed Postgres provider.
- This guide does not replace a security or compliance review.
