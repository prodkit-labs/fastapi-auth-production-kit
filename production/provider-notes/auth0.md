# Auth0 Migration Note

Use this note when deciding whether a local FastAPI auth path should move to Auth0.

Evidence status: `documented`

Reviewed sources:

- Auth0 authentication docs: https://auth0.com/docs/authentication
- Auth0 Universal Login docs: https://auth0.com/docs/authenticate/login/auth0-universal-login/new-experience

## When To Consider

Consider Auth0 when identity requirements are moving toward enterprise or multi-protocol needs.

Common signals:

- customers ask for SAML, OIDC, or enterprise identity workflows
- tenant-level settings matter
- MFA and login policy complexity is growing
- the product needs centralized login across multiple applications
- procurement or security review asks for mature identity controls

## What It Replaces

Auth0 may replace or absorb these local responsibilities:

- hosted login
- social and enterprise identity connections
- MFA policy surface
- tenant-level identity configuration
- parts of organization-aware login experiences
- identity-provider protocol handling

Your application still owns:

- product authorization and permissions
- tenant data model
- app-domain audit events
- account provisioning rules
- customer support policy

## Migration Impact

Before migrating, map:

- local users to Auth0 subject identifiers
- tenant or organization model
- callback and logout URLs
- token audience and issuer expectations
- backend token verification
- user metadata ownership

Enterprise identity usually changes support and onboarding workflows, not only login code.

## Watch Items

- configuration complexity
- tenant settings drift
- pricing and add-on costs
- SAML/OIDC implementation details
- how roles, permissions, and organizations map into your app

## Current Repo Fit

Use this repo to clarify which auth operations you are replacing and which product authorization rules must remain in FastAPI.

## Commercial Links

No affiliate or partner links are included in this note.
