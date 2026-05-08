# Security Policy

## Supported Versions

This project is currently in `v0.x`. Security fixes are applied to the `main` branch and the latest tagged release.

## Reporting A Vulnerability

Please do not open public issues for vulnerabilities involving:

- credential exposure
- token forgery
- token reuse
- account enumeration
- password reset bypass
- email verification bypass
- unsafe defaults
- provider integration issues

Use GitHub's private vulnerability reporting flow for this repository when available. If private reporting is unavailable, open a minimal public issue that says a private security report is needed, without sharing exploit details.

## Scope

This project is an educational production starter. It is not a replacement for a security review, compliance program, penetration test, or full identity platform.

## Local Development Defaults

Some settings intentionally expose verification and reset tokens for local development. They must be disabled outside local development.

## Production Warning

Before production use, review:

- `production/security-checklist.md`
- `production/deployment.md`
- `production/token-strategy.md`
- `production/provider-comparison.md`
