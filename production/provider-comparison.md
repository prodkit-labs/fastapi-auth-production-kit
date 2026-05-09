# Provider Comparison

This repo starts with local email/password auth so the open-source path remains usable without paid services.

Hosted auth can make sense when your product needs social login, enterprise identity, device/session management, admin consoles, or compliance-heavy audit trails.

Start with [build vs buy auth](build-vs-buy-auth.md) when the decision is still unclear.

## Evidence Labels

- `local`: covered by this repository's runnable examples and tests.
- `documented`: included as a decision option based on public product positioning and documentation.
- `needs review`: plausible fit, but this repo has not added hands-on integration notes.
- `not compared`: listed only as a category reference; no side-by-side evidence is included yet.

## Local Auth Path

| Path | Category | Evidence | Good Fit | Tradeoffs | Watch |
|---|---|---|---|---|---|
| Local FastAPI auth | Open-source starter | `local` | Small apps, internal tools, learning, full control | You own security operations | Secret handling, rate limits, resets, audit logs, token lifecycle |

## Hosted Auth UI

| Path | Category | Evidence | Good Fit | Tradeoffs | Watch |
|---|---|---|---|---|---|
| [Clerk](provider-notes/clerk.md) | Hosted auth UI | `documented` | SaaS apps that want polished hosted UI and account flows | More provider coupling | Pricing at scale, customization depth, migration path |
| [Supabase Auth](provider-notes/supabase-auth.md) | Hosted auth plus backend platform | `documented` | Apps already using Supabase database, storage, or edge functions | Platform coupling | Email settings, RLS design, local-to-hosted migration |
| [Logto](provider-notes/logto.md) | Open-source friendly identity platform | `documented` | Teams that want hosted or self-hosted identity with productized auth flows | Extra service to operate or adopt | Deployment model, upgrade path, integration maturity |
| Stytch | Hosted auth and identity APIs | `needs review` | Products exploring passwordless, passkeys, or identity API workflows | Provider-specific API design | Feature fit, account model, cost at scale |

## Enterprise Identity

| Path | Category | Evidence | Good Fit | Tradeoffs | Watch |
|---|---|---|---|---|---|
| [Auth0](provider-notes/auth0.md) | Enterprise identity and federation | `documented` | Enterprise identity, SAML/OIDC, tenant-level administration | Complex configuration | Tenant settings, SAML/OIDC details, cost model |
| WorkOS | Enterprise identity APIs | `needs review` | B2B SaaS needing SSO, directory sync, or enterprise onboarding | Adds a specialized identity dependency | Product scope, pricing, admin experience |

## Database And Deployment Adjacent

| Path | Category | Evidence | Good Fit | Tradeoffs | Watch |
|---|---|---|---|---|---|
| Supabase | Database and platform | `documented` | Teams wanting Postgres, auth, storage, and edge functions together | Platform coupling | RLS design, auth migration, email delivery settings |
| Neon | Managed Postgres | `not compared` | Apps keeping auth local but moving persistence to managed Postgres | Database only, not an auth provider | Connection pooling, migrations, backups |
| Railway | App and database deployment | `not compared` | Small teams deploying FastAPI and Postgres quickly | General platform dependency | Runtime settings, backups, networking, cost controls |
| Render | App and database deployment | `not compared` | Teams wanting managed web services and Postgres | General platform dependency | Runtime settings, backups, networking, cost controls |

## Email Delivery Adjacent

| Path | Category | Evidence | Good Fit | Tradeoffs | Watch |
|---|---|---|---|---|---|
| [Resend](provider-notes/resend.md) | Transactional email | `documented` | Verification and reset emails for developer-focused products | Email-only dependency | Deliverability, domain setup, monitoring |
| Postmark | Transactional email | `not compared` | Products that prioritize transactional deliverability | Email-only dependency | Templates, bounce handling, cost |
| SendGrid | Transactional and marketing email | `not compared` | Teams that already operate email programs there | Larger surface area | Domain reputation, templates, account configuration |

## Before Rankings

Provider rankings should not be added until this repo has:

- A published scoring rubric.
- A repeatable setup checklist for each provider.
- Hands-on integration notes for the compared providers.
- Versioned dates for product docs and pricing references.
- Clear separation between measured facts, maintainer opinion, and sponsor or partner relationships.

## Before Commercial Links

Commercial links should not be added until this repo has:

- Nearby disclosure text.
- A useful open-source path with no paid provider requirement.
- A real production decision context for the provider.
- No pay-to-rank placement.
- A changelog entry explaining where commercial links were introduced.

## Commercial Links

Affiliate or partner links may be added here only when they are tied to a real production decision and include nearby disclosure.

Do not add rankings without reproducible comparison data.
