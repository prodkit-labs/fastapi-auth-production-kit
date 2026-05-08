# Provider Comparison

This repo starts with local email/password auth so the open-source path remains usable without paid services.

Hosted auth can make sense when your product needs social login, enterprise identity, device/session management, admin consoles, or compliance-heavy audit trails.

| Path | Good fit | Tradeoffs | Watch |
|---|---|---|---|
| Local FastAPI auth | Small apps, internal tools, learning, full control | You own security operations | Secret handling, rate limits, resets, audit logs |
| Clerk | SaaS apps that need polished hosted UI | More provider coupling | Pricing at scale, customization needs |
| Auth0 | Enterprise identity and federation | Complex configuration | Tenant settings, cost, SAML/OIDC details |
| Supabase Auth | Apps already using Supabase | Platform coupling | Email settings, RLS design, migration path |
| Logto | Open-source friendly identity platform | Extra service to operate or host | Deployment, upgrades, integration maturity |

## Evidence Labels

- `local`: covered by this repository's runnable examples.
- `documented`: covered by public provider documentation.
- `not tested`: listed as a decision option, but no benchmark or integration evidence has been added.

## Commercial Links

Affiliate or partner links may be added here only when they are tied to a real production decision and include nearby disclosure.

Do not add rankings without reproducible comparison data.
