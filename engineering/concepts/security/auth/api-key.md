# API Key

An **API key** is an opaque, randomly-generated string that identifies a caller (a service, a developer, or an integration) and grants access to an API. Unlike a [JWT](jwt.md), an API key carries no embedded information — it is a lookup token: the server receives it, finds the matching record in its database, and reads the associated permissions, owner, and metadata from there.

A typical key looks like `sk-1234abcd5678efgh` or a 32–64 character hex/base62 string. The format is arbitrary — the only meaningful thing about it is that it is unguessable.

## How It Works

```
Client                              Server
  │                                   │
  │── GET /api/resource               │
  │   Authorization: Bearer sk-xxxx ──►│
  │                                   │── lookup sk-xxxx in DB
  │                                   │   read: owner, scopes, rate-limit, active?
  │◄─ 200 OK (or 401 if not found) ───│
```

Every request requires a DB lookup — the key itself proves nothing without consulting the record it points at.

## Key Properties

| Property | Value |
|---|---|
| **Structure** | Opaque — no inherent format, no encoded claims |
| **State** | Stateful — server must query DB to validate and retrieve permissions |
| **Expiry** | None built-in — must be implemented as a DB column (`expires_at`) |
| **Revocation** | Instant — delete or set `active = false` on the DB record |
| **Claims** | None carried in the token — permissions live in the DB row |
| **Transport** | Must be sent over [HTTPS](../../networking/https.md) — plaintext transmission exposes the key |
| **Standard** | No formal standard; common header: `Authorization: Bearer <key>` or `X-API-Key: <key>` |

## What a Key Record Looks Like

A minimal DB table for API keys:

```sql
CREATE TABLE api_keys (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash    TEXT NOT NULL UNIQUE,   -- SHA-256 or bcrypt hash, never the plaintext key
    owner_id    UUID NOT NULL,
    name        TEXT,                  -- human label: "Production integration", "CI runner"
    scopes      TEXT[],                -- e.g. ['read:documents', 'write:documents']
    rate_limit  INT,                   -- requests per minute, NULL = use global default
    active      BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now(),
    expires_at  TIMESTAMPTZ,           -- NULL = never expires
    last_used_at TIMESTAMPTZ
);
```

The **key itself is shown to the user once at creation and never stored plaintext**. Only the hash is stored. On each request: hash the incoming key, query by `key_hash`, check `active` and `expires_at`.

## Security Practices

**Hash in storage.** Never store the plaintext key. Use SHA-256 (fast, acceptable for high-entropy random strings that aren't passwords) or bcrypt (slower but appropriate if you want uniform treatment with passwords).

```python
import hashlib, secrets

def generate_api_key() -> tuple[str, str]:
    """Returns (plaintext_key_to_show_user, hash_to_store)."""
    key = "sk-" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, key_hash

def verify_api_key(incoming: str, stored_hash: str) -> bool:
    return hashlib.sha256(incoming.encode()).hexdigest() == stored_hash
```

**Send over [HTTPS](../../networking/https.md) only.** An API key in a plaintext [HTTP](../../networking/http.md) request is visible to any network intermediary.

**Scope and rate-limit per key.** A key for a read-only integration should only carry read scopes — it shouldn't be able to delete data even if the underlying owner could. Rate limits stored per-key let you throttle abusive integrations without affecting others.

**Allow instant revocation.** The primary reason to choose an API key over a [JWT](jwt.md) for long-lived integrations is exactly this: set `active = false` and the key is dead on the next request, no TTL to wait out.

**Audit log.** Update `last_used_at` on every successful auth. Emit structured log events with key ID, owner, endpoint, and timestamp — this is how you detect a leaked or abused key.

## Common Use Cases

- **Third-party developer access** — the standard model for public APIs (OpenAI `sk-` keys, Stripe keys, GitHub personal access tokens)
- **Service-to-service integrations** — a downstream service calling your API with a long-lived, scoped credential (no user context needed)
- **CLI tools and scripts** — automation pipelines that aren't acting on behalf of an interactive user
- **Webhook senders** — signing requests so the receiver can verify the payload came from a trusted source

## When Not to Use an API Key

- **User-facing web/mobile [authentication](authentication.md)** — you'd need to store the key on the client, where it can be extracted; [JWT](jwt.md) + short expiry is more appropriate
- **When you need to carry identity or role claims without a DB call** — [JWT](jwt.md) embeds the claims in the token itself; an API key always requires a lookup
- **When you need automatic expiry** — JWTs carry `exp` natively; an API key expiry must be managed explicitly

## Related

- [JWT](./jwt.md) — the stateless alternative: token carries signed claims, no DB lookup needed
- [Access Token + Refresh Token Pattern](access-refresh-tokens.md) — refresh tokens are structurally identical to API keys: opaque, DB-backed, instantly revocable
- [JWT vs API Key](../../../overviews/security/jwt-vs-api-key.md) — when to choose each
- [OAuth Scopes & Least-Privilege Tokens](./oauth-scopes.md) — scope model that applies to both
- [Secrets Management](../secrets/secrets-management.md) — storing and rotating credentials
- [Brute-Force Attacks](../attacks/brute-force.md) — [rate limiting](../../backend/architecture/rate-limiting.md) and lockout defenses that protect auth endpoints
