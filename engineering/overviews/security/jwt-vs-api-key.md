# JWT vs API Key

Two different mechanisms for authenticating callers to an API. They solve overlapping problems but with fundamentally different tradeoffs: [JWT](../../concepts/security/auth/jwt.md) embeds signed claims in the token itself (stateless), while an [API key](../../concepts/security/auth/api-key.md) is an opaque lookup handle (stateful).

## At a Glance

| Property | [JWT](../../concepts/security/auth/jwt.md) | [API Key](../../concepts/security/auth/api-key.md) |
|---|---|---|
| **Structure** | `header.payload.signature` — encoded, signed claims | Opaque random string — no inherent structure |
| **Validation** | Verify signature locally — no DB call needed | DB lookup required on every request |
| **State** | Stateless | Stateful |
| **Expiry** | Built-in `exp` claim (typically 15 min–24 h) | None built-in; must implement `expires_at` in DB |
| **Revocation** | Hard — requires a denylist or short TTL | Instant — set `active = false` in DB |
| **Carries claims** | Yes — user ID, roles, custom data baked in | No — permissions stored server-side, tied to key record |
| **Primary use** | User-facing auth, microservice identity propagation | Third-party integrations, service-to-service, CLI tools |
| **Standard** | RFC 7519 | No formal standard |

## When to Choose Which

| Scenario | Choose |
|---|---|
| User login session (web or mobile app) | [JWT](../../concepts/security/auth/jwt.md) |
| Microservice-to-microservice (no user context needed) | [API Key](../../concepts/security/auth/api-key.md) or mTLS |
| Third-party developer integrating your API | [API Key](../../concepts/security/auth/api-key.md) |
| Short-lived delegated access | [JWT](../../concepts/security/auth/jwt.md) with short `exp` |
| Need to identify "which user made this request" without a DB call | [JWT](../../concepts/security/auth/jwt.md) (`sub` claim) |
| Need instant revocation at any time | [API Key](../../concepts/security/auth/api-key.md) (delete or disable the DB record) |
| Self-hosted platform with user auth (e.g. [RAG](../../concepts/ai/rag/rag.md) system) | [JWT](../../concepts/security/auth/jwt.md) |
| Automation scripts, CI pipelines | [API Key](../../concepts/security/auth/api-key.md) |

## The Core Tradeoff

**[JWT](../../concepts/security/auth/jwt.md)**: The token is self-verifying. A correct signature on an unexpired token is all the evidence a service needs. This means no per-request DB hit — and it means you cannot undo a token that's already been issued, until it expires naturally or you maintain a denylist.

**[API Key](../../concepts/security/auth/api-key.md)**: The key is worthless without the DB record it points to. Every request pays a DB lookup. The payoff is complete, instant control: change or delete the record, and the key is dead on the next request, no TTL to wait out.

## Access Token + Refresh Token: The Standard Pattern

A single JWT with a long expiry is both a performance choice and a security liability. The industry standard splits it into two tokens with different lifetimes and storage rules.

**Access Token** — short-lived JWT
- Sent on every API request: `Authorization: Bearer <token>`
- TTL: 15 min – 1 hour
- Stateless — server verifies signature only, no DB call
- If stolen, the attacker's window is at most the TTL

**Refresh Token** — long-lived opaque token
- Sent only to the auth server's `/auth/refresh` endpoint, never to any other service
- TTL: days to weeks (matches "remember me" session length)
- Stored server-side as a DB record — same shape as an API key, can be revoked instantly
- Should be stored in an `httpOnly` cookie; JS cannot read it, so [XSS](../../concepts/security/attacks/xss.md) cannot steal it

**The flow:**

```
1. POST /auth/login  →  access_token (15 min) + refresh_token (7 days, httpOnly cookie)
2. Client sends access_token on every request
3. 401 Unauthorized (token expired)
4. POST /auth/refresh (refresh_token in cookie)  →  new access_token
5. Client retries original request with new access_token
```

**Refresh token rotation** — on each `/auth/refresh` call:
1. Old refresh token is invalidated immediately
2. A new refresh token is issued alongside the new access token
3. If an attacker steals a refresh token and uses it first, the legitimate user's next refresh hits an already-invalidated token — the server detects reuse and can revoke the entire session family as a theft signal

**Storage rules:**

| Token | Store in | Why |
|---|---|---|
| Access token | In-memory (JS variable, React state) | Short-lived; losing it on page reload is fine; can't be stolen via [XSS](../../concepts/security/attacks/xss.md) without a separate exfil vector |
| Refresh token | `httpOnly` cookie | JS cannot read `httpOnly` cookies → [XSS](../../concepts/security/attacks/xss.md) cannot steal it |

**Common mistake: refresh token in `localStorage`**  
`localStorage` is readable by any script on the page. An [XSS](../../concepts/security/attacks/xss.md) payload can silently exfiltrate a refresh token, giving an attacker persistent access even after the access token expires. Use `httpOnly` cookies instead.

---

## Common Mistake: Long-Lived JWTs Without a Revocation Path

Issuing a JWT with a 30-day expiry and no denylist means a stolen token is valid for up to 30 days and there is nothing you can do about it. The standard mitigation:

- Keep access tokens short-lived (15 min)
- Pair with a refresh token (long-lived, stored server-side, can be revoked)
- On sensitive permission changes (role change, account disable), implement the `tokenVersion` counter pattern so the next request forces re-[authentication](../../concepts/security/auth/authentication.md)

See [JWT — Revoking a Token You Can't Un-issue](../../concepts/security/auth/jwt.md#revoking-a-token-you-cant-un-issue) for implementation details.

## In Practice: RAG Platform Authentication

In a [vLLM](../../concepts/ai/infrastructure/vllm.md) [RAG](../../concepts/ai/rag/rag.md) Chat Platform:

- Users authenticate with username/password → receive a **short-lived JWT** (contains `user_id`, `roles`, `exp`)
- The JWT is sent as `Authorization: Bearer <token>` on each request
- The [FastAPI](../../concepts/programming/python/fastapi.md)/NestJS gateway verifies the signature locally — no DB call — and extracts `user_id` to scope the chat session and document permissions
- Third-party integrations (e.g. a customer embedding the chat widget) use an **API key** tied to their organization record — long-lived, instantly revocable, scoped to `read:documents`

This gives the system both: stateless user auth at scale, and manageable third-party credentials.

## Atomic Notes

- [JWT](../../concepts/security/auth/jwt.md) — structure, signing algorithms, revocation, stale claims, `tokenVersion` pattern
- [API Key](../../concepts/security/auth/api-key.md) — key record schema, hashing, scoping, use cases
- [Access Token + Refresh Token Pattern](../../concepts/security/auth/access-refresh-tokens.md) — the standard two-token session pattern: short-lived JWT access token + long-lived DB-backed refresh token with rotation and theft detection

## Related

- [OAuth Scopes & Least-Privilege Tokens](../../concepts/security/auth/oauth-scopes.md)
- [Access Control & IAM](../../concepts/security/authorization/access-control-iam.md)
- [Secrets Management](../../concepts/security/secrets/secrets-management.md)
- [Guards](../../concepts/backend/nestjs/guards.md)
