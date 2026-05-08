# Architecture

The kit keeps auth code in a few replaceable layers.

| Layer | File | Responsibility |
|---|---|---|
| API | `routes.py` | HTTP routes and bearer-token dependency |
| Service | `service.py` | User registration and authentication decisions |
| Security | `security.py` | Password hashing and JWT helpers |
| Database | `database.py` | SQLite connection and schema setup |
| SQLAlchemy track | `sqlalchemy_track.py` | Optional model and session pattern for production databases |
| Settings | `config.py` | Environment-driven configuration |

The boundary is intentionally small. A production app can replace SQLite, swap JWT settings, or move to hosted auth without rewriting route handlers across the whole codebase.

Email verification and password reset use separate JWT purpose claims so access tokens cannot be reused for account-change flows. The local routes can expose verification and reset tokens for development; production apps should send those tokens through an email flow and disable token exposure.

The starter keeps login available for unverified users by default so the quickstart stays simple. Set `AUTH_REQUIRE_VERIFIED_EMAIL_FOR_LOGIN=true` when your product should block login until verification is complete.

The SQLAlchemy track is kept separate from the default app so local SQLite remains easy to inspect. Use `production/sqlalchemy-postgres.md` when you are ready to move auth data into managed Postgres.
