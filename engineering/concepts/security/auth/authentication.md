# Authentication

**Authentication** answers one question: **who are you?** It's the process of verifying that an identity claim (a username, an email, a token) actually belongs to the party presenting it — a login form checking a password, a server validating a signed token, a mobile app confirming a fingerprint. Authentication is the first of three distinct questions an access-control system has to answer; it says nothing by itself about what that verified identity is then allowed to *do* — that's [authorization](../authorization/authorization.md)'s job.

## Authentication vs. Authorization — The Distinction That Matters Most

These two terms are constantly confused because they're adjacent steps in the same flow, but they answer completely different questions:

| | Authentication | [Authorization](../authorization/authorization.md) |
|---|---|---|
| **Question** | Who are you? | What are you allowed to do? |
| **Checked against** | Credentials (password, token signature, biometric) | Permissions/roles/policies |
| **Happens** | First, once per session/request | After authentication, per action/resource |
| **Failure result** | 401 Unauthorized (identity not established) | 403 Forbidden (identity known, action denied) |
| **Example mechanisms** | Password login, [JWT](jwt.md), [OAuth](oauth-scopes.md), [OTP](otp.md)/MFA | [RBAC](../authorization/rbac.md), [CASL](../authorization/casl.md), [OpenFGA](../authorization/openfga.md) |

A useful shorthand: authentication is the bouncer checking your ID at the door; [authorization](../authorization/authorization.md) is the staff deciding which rooms your ticket lets you into once you're inside. You can be authenticated (the bouncer confirms you're really you) and still be unauthorized (your ticket doesn't cover the VIP room) — the two checks are independent and both required.

## The Authentication Flow

```
1. Client presents credentials (password, API key, biometric, or an existing token)
2. Server verifies those credentials against a trusted source
   (a password hash in a database, a token's cryptographic signature, an identity provider)
3. If valid: server establishes a session or issues a token proving "this identity is verified"
4. That proof (session cookie / token) is presented on every subsequent request
   so step 1-2 don't need to repeat for every single call
```

The step that actually distinguishes authentication mechanisms from each other is step 2 — *what* is being verified and *how*:

| Mechanism | What's verified | Where it's covered |
|---|---|---|
| **Password login** | A secret only the user should know, hashed and compared | Session-based auth, the oldest pattern |
| **[JWT](jwt.md)** | A cryptographic signature on a self-contained token — no DB lookup needed to verify | [JWT](jwt.md) |
| **[API Key](api-key.md)** | A long-lived static secret, usually for service-to-service or third-party API access | [API Key](api-key.md) |
| **[OAuth](oauth-scopes.md)** | Delegated authentication via a third-party identity provider (Google, GitHub, [Microsoft Entra ID](../../cloud/azure/microsoft-entra-id.md)) | [OAuth Scopes & Least-Privilege Tokens](oauth-scopes.md) |
| **[OTP](otp.md) / MFA** | A second factor beyond the primary credential — time-limited code, authenticator app, SMS | [One-Time Passwords (OTP)](otp.md) |
| **[Access/Refresh Tokens](access-refresh-tokens.md)** | A short-lived access token plus a longer-lived refresh token, so re-authentication isn't needed on every expiry | [Access Token + Refresh Token Pattern](access-refresh-tokens.md) |
| **[HMAC](../secrets/hmac.md)** | A request signature proving the sender holds a shared secret, without transmitting the secret itself | [HMAC](../secrets/hmac.md) |

## Authentication Practices That Matter in Production

- **Password hashing, never plaintext** — store a one-way hash (bcrypt/argon2/scrypt), never the password itself; a leaked database then reveals nothing directly usable.
- **Brute-force protection** — rate-limit or lock out repeated failed login attempts per account/IP, or an attacker can simply guess passwords at scale.
- **Session timeout** — sessions/tokens should expire after inactivity, limiting the window a stolen session cookie or token stays useful.
- **[HTTPS](../../networking/https.md) enforcement** — credentials and tokens must never travel over plain [HTTP](../../networking/http.md), or they're trivially interceptable in transit.
- **Multi-factor authentication (MFA)** — a password alone is a single point of failure; requiring a second factor ([OTP](otp.md), authenticator app) means a leaked password alone isn't enough to authenticate as the victim.

## Where Authentication Fits in a Larger System

Authentication is step one of [IAM (Identity and Access Management)](../authorization/access-control-iam.md)'s three questions — who are you, what can you do, what did you do — and it's the gate everything else in an access-controlled system sits behind: [authorization](../authorization/authorization.md) checks are meaningless without a verified identity to check permissions against in the first place, and audit logging needs that same verified identity to attribute actions to the right actor.

In an enterprise [RAG](../../ai/rag/rag.md) system specifically, authentication establishes *who* is asking a question before [authorization](../authorization/authorization.md) decides which documents that identity is permitted to have retrieved into the answer — skipping or weakening authentication at the API layer makes every downstream permission check moot, since there's no reliable identity to check permissions against.

## Related

- [Authorization](../authorization/authorization.md) — the next question, answered only after authentication succeeds
- [Access Control & IAM](../authorization/access-control-iam.md) — the fuller framework (authN + authZ + audit) this file is one-third of
- [JWT](jwt.md) — the most common stateless authentication token format
- [OAuth Scopes & Least-Privilege Tokens](oauth-scopes.md) — delegated authentication via a third-party identity provider
- [One-Time Passwords (OTP)](otp.md) — the multi-factor-authentication mechanism
- [API Key](api-key.md) — the simpler, longer-lived alternative to token-based auth
- [Access Token + Refresh Token Pattern](access-refresh-tokens.md)
- [HMAC](../secrets/hmac.md) — signature-based authentication without transmitting the secret
- [Microsoft Entra ID](../../cloud/azure/microsoft-entra-id.md) — a concrete managed identity provider implementing authentication at cloud scale
