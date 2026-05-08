# Architecture

The kit keeps auth code in a few replaceable layers.

| Layer | File | Responsibility |
|---|---|---|
| API | `routes.py` | HTTP routes and bearer-token dependency |
| Service | `service.py` | User registration and authentication decisions |
| Security | `security.py` | Password hashing and JWT helpers |
| Database | `database.py` | SQLite connection and schema setup |
| Settings | `config.py` | Environment-driven configuration |

The boundary is intentionally small. A production app can replace SQLite, swap JWT settings, or move to hosted auth without rewriting route handlers across the whole codebase.

Password reset uses a separate JWT purpose claim so access tokens cannot be reused as reset tokens. The local route can expose reset tokens for development; production apps should send those tokens through an email flow and disable token exposure.
