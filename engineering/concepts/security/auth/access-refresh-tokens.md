# Access Token + Refresh Token Pattern

The access token + refresh token pattern is the industry-standard approach to giving a user a persistent authenticated session while keeping the credential that travels on every API request short-lived and revocable. It splits the session into two tokens with different lifetimes, storage locations, and trust scopes.

## The Two Tokens

**Access Token**
- Short-lived [JWT](jwt.md) sent on every API request as `Authorization: Bearer <token>`
- TTL: 15 min – 1 hour
- Stateless validation — server checks the signature only, no DB call
- Carries claims: `sub` (user ID), `roles`, `exp`, `iat`
- When expired, the client silently exchanges the refresh token for a new one

**Refresh Token**
- Long-lived opaque token (structurally similar to an [API key](api-key.md) — random string, DB-backed)
- TTL: days to weeks; matches the "remember me" / session-length requirement
- Stored server-side as a DB record — can be revoked instantly by setting `active = false`
- Sent **only** to the auth server's `/auth/refresh` endpoint, never to other services
- Should be stored in an `httpOnly` cookie on the client (JS cannot read it → [XSS](../attacks/xss.md)-resistant)

## Authentication Flow

```
1. POST /auth/login
   → server issues: access_token (15 min JWT) + refresh_token (7 days, stored as httpOnly cookie)

2. Client sends access_token in Authorization header on every request

3. Server returns 401 (token expired)
   → client silently calls POST /auth/refresh with the refresh_token cookie

4. Server validates refresh token (DB lookup), issues:
   - new access_token
   - new refresh_token (if using rotation)

5. Client retries the original request with the new access_token
```

## Refresh Token Rotation

Each time `/auth/refresh` is called:

1. The old refresh token is immediately invalidated in the DB
2. A new refresh token is issued
3. A new access token is issued

**Why this matters:** if an attacker steals a refresh token and uses it before the legitimate user does, the legitimate user's next refresh call presents an already-invalidated token. The server detects **reuse of an invalidated token** and can revoke the entire token family (all refresh tokens for that session) as a theft signal. Without rotation, a stolen refresh token is a permanent credential until it expires or the user explicitly logs out.

## Storage Rules

| Token | Store in | Why |
|---|---|---|
| Access token | Memory (JS variable, React state) | Short-lived; losing it on page reload is fine; no [XSS](../attacks/xss.md) risk without a separate exfil vector |
| Refresh token | `httpOnly` cookie | JS cannot read `httpOnly` cookies → [XSS](../attacks/xss.md) cannot steal it |

## Common Mistakes

- **Storing the refresh token in `localStorage`** — readable by any script on the page; an [XSS](../attacks/xss.md) payload can silently exfiltrate it, giving persistent access even after the short-lived access token expires
- **Long-lived access tokens (hours/days) with no refresh mechanism** — defeats the purpose of short TTLs; a stolen token is valid for the full duration with no way to revoke it
- **Sending the refresh token to non-auth services** — it should only ever reach `/auth/refresh`; if it leaks via a misrouted request, the attacker gets persistent access
- **Not implementing rotation** — a static refresh token that never changes is a permanent credential if stolen; rotation limits the damage window and enables theft detection

## DB Schema for a Refresh Token Record (Prisma Example)

```prisma
model RefreshToken {
  id           String   @id @default(cuid())
  tokenHash    String   @unique  // SHA-256 hash of the token value
  userId       String
  user         User     @relation(fields: [userId], references: [id])
  active       Boolean  @default(true)
  familyId     String   // group tokens for rotation reuse-detection
  expiresAt    DateTime
  createdAt    DateTime @default(now())
  replacedById String?  // points to successor token on rotation

  @@index([userId])
  @@index([familyId])
}
```

Key design decisions:
- `tokenHash` — store a SHA-256 hash of the random token value, never the plaintext (same principle as [API key](api-key.md) storage)
- `familyId` — groups all tokens descended from a single login; detecting reuse of any invalidated token in the family triggers revocation of the entire family
- `replacedById` — creates an auditable chain of rotation; useful for forensics after a theft event

## Related

- [JWT](jwt.md) — the access token format: structure, claims, signing, stale-claims pattern, `tokenVersion` revocation
- [API Key](api-key.md) — refresh tokens are structurally similar: opaque, DB-backed, instantly revocable
- [JWT vs API Key](../../../overviews/security/jwt-vs-api-key.md) — where the access+refresh pattern fits in the bigger picture
