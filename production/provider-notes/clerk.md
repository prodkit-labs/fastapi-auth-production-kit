# Clerk Migration Note

Use this note when deciding whether a local FastAPI auth path should move to Clerk.

Evidence status: `documented`

Reviewed sources:

- Clerk docs: https://clerk.com/docs/

## When To Consider

Consider Clerk when your product needs a hosted auth UI and managed account flows sooner than your team can safely build them.

Common signals:

- sign-in and sign-up UI are taking time away from core product work
- the product needs organization or team accounts
- the team wants managed session options, MFA, password policies, or bot protection
- frontend account-management polish matters more than keeping every auth surface local

## What It Replaces

Clerk may replace or absorb these local responsibilities:

- registration and login UI
- password reset and account recovery UI
- email verification UI
- session handling
- parts of organization membership
- parts of MFA and account security policy

Your application still owns:

- app-specific authorization rules
- product roles and entitlements
- database mapping between provider user ids and app records
- support policy and data deletion workflow
- incident response for your product data

## Migration Impact

Before migrating, map:

- local `users.id` to provider user id
- user email normalization
- verified-email semantics
- organization or team membership model
- how bearer tokens or cookies reach the FastAPI backend
- logout and session invalidation expectations

Do not assume a hosted provider removes the need for backend authorization checks.

## Watch Items

- pricing at scale
- coupling to provider-specific frontend components and session model
- customization limits for account flows
- export and rollback path
- audit-log and compliance requirements for your customer segment

## Current Repo Fit

This repo remains useful before or during a Clerk migration because it documents:

- local auth responsibilities
- token strategy questions
- production handoff checklist
- build-vs-buy decision criteria

## Commercial Links

No affiliate or partner links are included in this note.
