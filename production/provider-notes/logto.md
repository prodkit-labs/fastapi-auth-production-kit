# Logto Migration Note

Use this note when deciding whether a local FastAPI auth path should move to Logto.

Evidence status: `documented`

Reviewed sources:

- Logto introduction: https://docs.logto.io/introduction
- Logto enterprise SSO docs: https://docs.logto.io/end-user-flows/enterprise-sso

## When To Consider

Consider Logto when you want an identity platform with open-source-friendly positioning and a choice between hosted or self-managed identity operations.

Common signals:

- the product needs productized sign-in and account flows
- enterprise SSO is on the roadmap
- the team wants an identity service boundary instead of auth logic embedded in the FastAPI app
- self-hosting or deployment control is part of the evaluation

## What It Replaces

Logto may replace or absorb these local responsibilities:

- sign-in and sign-up experience
- auth flow configuration
- social login setup
- enterprise SSO integration
- parts of account security and organization experience

Your application still owns:

- product authorization model
- user-to-domain-object mapping
- operational responsibility if self-hosting
- data retention and support policy
- provider upgrade and backup process

## Migration Impact

Before migrating, map:

- local users to Logto identities
- application and API resource model
- organization or tenant expectations
- token validation in FastAPI
- self-hosted versus cloud operating model
- rollback path if provider assumptions change

## Watch Items

- deployment and upgrade responsibility when self-hosting
- integration maturity for your framework and user model
- enterprise SSO setup details
- cost and operational model at scale

## Current Repo Fit

Use this repo to define the local auth responsibilities you want Logto to remove and the product authorization rules that should remain in FastAPI.

## Commercial Links

No affiliate or partner links are included in this note.
