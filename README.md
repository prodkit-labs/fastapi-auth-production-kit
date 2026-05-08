# FastAPI Auth Production Kit

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-auth%20starter-009688)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
[![Test](https://github.com/prodkit-labs/fastapi-auth-production-kit/actions/workflows/test.yml/badge.svg)](https://github.com/prodkit-labs/fastapi-auth-production-kit/actions/workflows/test.yml)

A FastAPI starter for building authentication that survives the first production handoff.

Most auth examples stop at "register and login." This repo focuses on what teams need next: password hashing, JWT access tokens, route protection, SQLite persistence, testable settings, deployment notes, and decision guides for when to use hosted auth instead.

This kit helps you answer:

- How should a small FastAPI app structure auth without spreading security logic everywhere?
- What can run locally with no paid services?
- Which checks should exist before moving auth into production?
- When is a hosted auth provider worth considering?

Ships today:

- FastAPI app factory
- SQLite user store
- Password hashing with `passlib`
- JWT access tokens with `python-jose`
- Protected `/me` route
- Environment-driven settings
- Email verification flow with signed expiring tokens
- Password reset flow with signed expiring tokens
- Pytest coverage for register, login, email verification, password reset, duplicate users, and protected routes
- Production docs for deployment, provider comparison, security checklist, and disclosure

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
uvicorn prodkit_auth.main:app --reload
```

Create a user:

```bash
curl -s http://127.0.0.1:8000/auth/register \
  -H 'content-type: application/json' \
  -d '{"email":"dev@example.com","password":"correct horse battery staple"}'
```

Login:

```bash
curl -s http://127.0.0.1:8000/auth/login \
  -H 'content-type: application/json' \
  -d '{"email":"dev@example.com","password":"correct horse battery staple"}'
```

Use the returned token:

```bash
curl -s http://127.0.0.1:8000/me \
  -H "authorization: Bearer $ACCESS_TOKEN"
```

Request an email verification token for local development:

```bash
curl -s http://127.0.0.1:8000/auth/email-verification/request \
  -H 'content-type: application/json' \
  -d '{"email":"dev@example.com"}'
```

Confirm the email:

```bash
curl -s http://127.0.0.1:8000/auth/email-verification/confirm \
  -H 'content-type: application/json' \
  -d '{"token":"VERIFICATION_TOKEN"}'
```

The request endpoint returns `verification_token` by default so the local example is runnable without an email provider. Set `AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=false` before adapting the flow for production email delivery.

Request a password reset token for local development:

```bash
curl -s http://127.0.0.1:8000/auth/password-reset/request \
  -H 'content-type: application/json' \
  -d '{"email":"dev@example.com"}'
```

Confirm the reset:

```bash
curl -i http://127.0.0.1:8000/auth/password-reset/confirm \
  -H 'content-type: application/json' \
  -d '{"token":"RESET_TOKEN","new_password":"new correct horse battery staple"}'
```

The request endpoint returns `reset_token` by default so the local example is runnable without an email provider. Set `AUTH_EXPOSE_RESET_TOKEN=false` before adapting the flow for production email delivery.

## What You Can Run Today

| Workflow | Command | Output |
|---|---|---|
| Test auth flow | `pytest` | Register/login/email-verification/password-reset/protected-route coverage |
| Run API locally | `uvicorn prodkit_auth.main:app --reload` | Local FastAPI server |
| Inspect OpenAPI | Open `/docs` | Interactive route docs |

## Architecture

The kit uses a narrow service layer so database access, token handling, and route handlers stay easy to replace.

```text
src/prodkit_auth/
  main.py          FastAPI app factory and default app
  config.py        Environment-driven settings
  database.py      SQLite connection and schema setup
  security.py      Password hashing and JWT helpers
  schemas.py       Request and response models
  service.py       User registration and authentication
  routes.py        API routes and bearer-token dependency
```

## Production Guides

- [Security checklist](production/security-checklist.md)
- [Deployment](production/deployment.md)
- [Provider comparison](production/provider-comparison.md)
- [Disclosure policy](production/disclosure.md)
- [Roadmap](ROADMAP.md)

## Non-Goals

This repo is not a replacement for a security review, a compliance program, or a full identity platform. It intentionally starts with local email/password auth so the open-source path remains runnable without paid services.

For production systems, review the security checklist before adapting the code.

## License

MIT
