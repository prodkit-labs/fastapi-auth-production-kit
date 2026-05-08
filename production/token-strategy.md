# Token Strategy

## Current Local Path

- Short-lived bearer access tokens.
- HS256 signing.
- `sub` and `exp` claims on access tokens.
- Separate `purpose` claims for email verification and password reset tokens.
- Stateless verification and reset tokens for simple local development.

## Before Production

- Set a unique `AUTH_SECRET_KEY`.
- Use HTTPS everywhere.
- Decide whether tokens should live in bearer headers or secure cookies.
- Add `iss` and `aud` when multiple services consume tokens.
- Add `iat`, `nbf`, and `jti` when token replay or revocation matters.
- Add refresh-token rotation when users need long sessions.
- Add a server-side token version if password changes should invalidate active sessions.
- Store reset and verification token hashes server-side when single-use behavior is required.

## Reset And Verification Tokens

The current reset and verification flows are intentionally stateless. That keeps the local path easy to run, but it means tokens can be reused until they expire.

For production-sensitive systems, add stateful token tables:

```text
auth_action_tokens
  id
  user_id
  token_hash
  purpose
  expires_at
  used_at
  created_at
  request_ip_hash
  user_agent_hash
```

Only store token hashes. Return the token once, send it through email, and mark it used after a successful action.

## When To Use Hosted Auth

Use hosted auth when you need:

- social login
- MFA
- organization membership
- SAML/OIDC
- device and session management
- admin consoles
- audit logs
- compliance-oriented identity workflows
