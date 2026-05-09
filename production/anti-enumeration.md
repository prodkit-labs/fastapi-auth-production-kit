# Anti-Enumeration Registration

Registration can reveal account existence when duplicate emails return a different status code or response body.

This kit keeps the local default explicit so demos and client integrations are easy to understand:

```text
AUTH_REGISTRATION_ENUMERATION_MODE=explicit
```

In explicit mode, duplicate registration returns `409 Conflict`.

For sensitive products, switch to generic mode:

```text
AUTH_REGISTRATION_ENUMERATION_MODE=generic
```

In generic mode, registration always returns `201 Created` with a normalized response:

```json
{
  "id": 0,
  "email": "dev@example.com",
  "is_verified": false
}
```

The server still creates a real user when the email is new. When the email already exists, it returns the same response shape without exposing the stored user id or verification state.

## Production Notes

- Pair generic registration with rate limits on `/auth/register`.
- Keep password reset and email verification request responses generic.
- Send verification and reset links only through monitored email delivery.
- Record structured account events in a private audit trail.
- Consider hosted auth when you need MFA, social login, enterprise identity, organization membership, or session administration.
