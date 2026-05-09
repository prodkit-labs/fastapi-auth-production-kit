# Resend Email Delivery Note

Use this note when deciding whether local verification and reset token previews should become real transactional email delivery through Resend.

Evidence status: `documented`

Reviewed sources:

- Resend domain docs: https://resend.com/docs/dashboard/domains/introduction
- Resend sender note: https://resend.com/docs/knowledge-base/how-do-I-create-an-email-address-or-sender-in-resend
- Resend and Supabase guide: https://resend.com/docs/knowledge-base/getting-started-with-resend-and-supabase

## When To Consider

Consider Resend when local reset and verification token previews need to become real email delivery for a developer-focused product.

Common signals:

- `AUTH_EXPOSE_RESET_TOKEN` and `AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN` are ready to be disabled
- the product needs domain-based transactional email
- reset and verification emails need delivery monitoring
- developer experience matters for email API integration

## What It Replaces

Resend does not replace authentication. It may replace only the local token preview path:

- sending verification emails
- sending password reset emails
- managing domain-based sender setup
- tracking delivery-related operational work

Your application still owns:

- token generation and validation
- reset and verification route behavior
- abuse monitoring and resend limits
- account recovery support policy
- user-facing email content

## Migration Impact

Before migrating, map:

- which domain or subdomain sends auth email
- DNS ownership and domain verification
- reset and verification link construction
- email template ownership
- bounce and delivery monitoring
- secret storage for the email API key

Disable local token exposure before treating email delivery as production-ready.

## Watch Items

- DNS setup and sender reputation
- whether auth email should use a separate subdomain
- sensitive data in email content
- bounce and complaint handling
- provider outage behavior

## Current Repo Fit

This repo already has reset and verification token flows. Resend would sit at the delivery layer after the token and route policies are chosen.

## Commercial Links

No affiliate or partner links are included in this note.
