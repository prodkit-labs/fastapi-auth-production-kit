# Supabase Auth Migration Note

Use this note when deciding whether a local FastAPI auth path should move to Supabase Auth.

Evidence status: `documented`

Reviewed sources:

- Supabase Auth docs: https://supabase.com/docs/guides/auth
- Supabase MFA docs: https://supabase.com/docs/guides/auth/auth-mfa

## When To Consider

Consider Supabase Auth when your app is already moving toward the Supabase platform or when auth, Postgres, storage, and edge functions should live together.

Common signals:

- the product already uses Supabase Postgres
- Row Level Security design is central to the app
- the team wants auth close to the database layer
- OAuth/OIDC provider support is enough for the product's near-term needs
- platform consolidation matters more than keeping auth fully local

## What It Replaces

Supabase Auth may replace or absorb these local responsibilities:

- user management
- sign-up and sign-in APIs
- OAuth provider configuration
- email confirmation and password reset delivery path
- MFA flows supported by the platform
- JWT issuing for Supabase-integrated resources

Your application still owns:

- FastAPI authorization logic
- profile tables and app-specific user data
- RLS policy design when using Supabase Postgres
- support workflow
- migration and data-portability planning

## Migration Impact

Before migrating, map:

- local user ids to Supabase auth users
- profile table ownership
- JWT verification strategy in FastAPI
- email template and delivery behavior
- RLS policy boundaries
- whether FastAPI remains the main API or becomes an integration layer

## Watch Items

- platform coupling
- RLS design mistakes
- email settings and deliverability
- pricing dimensions such as active users or add-ons
- local-to-hosted rollback path

## Current Repo Fit

The local starter is still useful as a reference for FastAPI-side authorization, account policies, and production handoff decisions even when Supabase owns identity.

## Commercial Links

No affiliate or partner links are included in this note.
