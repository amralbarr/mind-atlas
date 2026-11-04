# JWT (JSON Web Tokens)

A JWT is a compact, self-contained token format for representing claims (facts about who's calling and what they're allowed to do) that a server can verify without a database lookup — the signature alone proves the claims haven't been tampered with since issuance.

## Structure

A JWT is three base64url-encoded segments joined by dots: `header.payload.signature`.

| Segment       | Contains                                                                                                  |
| ------------- | --------------------------------------------------------------------------------------------------------- |
| **Header**    | Algorithm (`alg`) and token type (`typ`) — e.g. `{"alg": "HS256", "typ": "JWT"}`                          |
| **Payload**   | The claims — arbitrary key/value data, plus a set of registered claim names with standard meaning         |
| **Signature** | [HMAC](../secrets/hmac.md) or public-key signature over `header + payload`, using a secret or private key only the issuer holds |

Anyone can *decode* a JWT's payload (it's just base64, not encrypted) — the signature is what prevents *forging or modifying* it undetected. Never put secrets in a JWT payload for this reason.

## Common Registered Claims

| Claim | Meaning |
|---|---|
| `iss` | Issuer — who minted this token |
| `aud` | Audience — who this token is intended for; a service should reject a token whose `aud` doesn't name it |
| `sub` | Subject — the identity the token represents (usually a user id) |
| `exp` | Expiry — unix timestamp after which the token is invalid |
| `nbf` | Not-before — token isn't valid until this time |
| `iat` | Issued-at |
| `jti` | JWT ID — a unique id per token, useful for reserving future revocation/denylist capability even if not used yet |
| `kid` | Key ID (header claim) — which signing key to verify against, enabling key rotation without a format change |

## Symmetric vs. Asymmetric Signing

| | Symmetric (HS256) | Asymmetric (RS256 / ES256) |
|---|---|---|
| Keys | One shared secret signs and verifies | A private key signs, a public key verifies |
| Use case | Signer and verifier are the same service (or trust each other with the shared secret) | Verifier is a different service than the signer, or many services need to verify without holding a signing secret |
| Rotation | Rotating the secret invalidates every unexpired token at once unless versioned via `kid` | A new keypair can be introduced via `kid` while the old public key still verifies older tokens |

## A Core Best Practice: Don't Let One Verifier Handle Multiple Token Classes

RFC 8725 (JWT Best Current Practices) recommends that structurally different classes of token — e.g. a long-lived admin session token vs. a short-lived, narrowly-scoped guest token — use **different signing keys, and ideally a structurally separate verification function**, not a single verifier that branches on a payload claim (like `if (payload.typ === 'guest') {...}`). A branch-based design means a bug in that one `if` can let a narrow-privilege token be treated as a full-privilege one; separate keys and separate verifier code paths make that class of bug structurally impossible, not just unlikely.

**Real-world example**: A real third-party embeddable-widget design documents exactly this fix — an initial design branched a new "embed" token class through the same verifier already used for admin session tokens (via a `typ` claim check), and an external security review flagged it as the design's single biggest weakness. The revision introduced a second, dedicated `JwtService` instance with its own signing key, its own `aud`/`iss`/`token_use` checks, and a verifier that the original session-token code path never calls at all — so a bug in the new verifier cannot, by construction, cause the original one to incorrectly succeed.

## Revoking a Token You Can't "Un-issue"

A stateless JWT is normally valid until `exp`, with no way to invalidate it early — that's the tradeoff for not needing a database lookup per request. Two common ways to add early revocation back in:

- **A denylist** — store revoked `jti` values (e.g. in Redis with a TTL matching the token's own `exp`) and check membership on each request; this reintroduces a stateful lookup, deliberately, only for the revocation check.
- **Live status on the *issuing entity*, not the token** — instead of a per-token denylist, check a cheap, cacheable status flag on whatever minted the token (an [API key](api-key.md)'s status, a user's account status). This gives coarser-grained revocation ("kill every token this key ever issued") without a per-token store, and composes well with `kid`/`key_id`-style claims that identify which entity minted a given token.

## Stale Claims: A Different Problem From Revocation

Revocation asks "should this token still work at all?" A subtler, more commonly-hit problem: the token still verifies fine (signature valid, not expired, not revoked) but a claim it carries — most often a **role or permission level**, baked in at login — no longer matches reality, because the underlying record changed *after* the token was issued. Promoting or demoting a user, or disabling their account, has no effect until that user's token is naturally replaced (next login, or a refresh-token exchange) — a token minted an hour before a demotion keeps acting on the old role for the rest of its lifetime. This is easy to miss because nothing is "broken" in the traditional sense: every check the verifier runs still passes, so no error, log line, or test catches it — the system is just quietly enforcing yesterday's permissions.

**Why this is so easy to introduce accidentally**: a JWT-based auth flow that only *decodes* the token on each request (checks signature + `exp`, reads claims straight out of the payload) — with no per-request database read of the user record at all — has no mechanism to notice that the source data changed. That's the entire point of a stateless token, which is exactly what makes this a structural blind spot rather than a bug in any single line of code.

### The `tokenVersion` Pattern

A common fix that closes both the stale-claims problem *and* doubles as cheap revocation, without a full denylist or session store:

1. Add a small integer/counter column to the user record (`tokenVersion`, starting at `0` or `1`).
2. Embed the current value as a claim in the JWT at issue time.
3. On each request (or each cache-miss — see below), compare the token's `tokenVersion` claim against the *current* value on the record; mismatch → reject, forcing re-[authentication](authentication.md).
4. **Increment the counter** any time something a token asserts becomes stale: a role/permission change, disabling the account, a forced logout-everywhere action, a password reset.

This single mechanism covers role-change staleness, account-disable staleness, and full revocation ("log this user out of every device right now") all at once, because all three are really the same underlying problem — a claim the token carries no longer matches the source of truth — with a single counter as the source-of-truth pointer.

**The cost, and how to keep it small**: naively, this reintroduces a database read on every single request, which is exactly what a stateless JWT was chosen to avoid. In practice this is made cheap with a short-TTL cache (tens of seconds) in front of the version check — a role change then takes effect within that TTL window rather than instantly, which is a reasonable trade for avoiding a DB round-trip on every authenticated request. This is the same "live status on the issuing entity, cached briefly" shape described above, just scoped to a per-user counter instead of a per-key/per-app status flag.

**Why not just shorten the token's `exp` instead?** A shorter expiry narrows the staleness window but never closes it, and does nothing for a "remember me"-style long-lived session, which by design is meant to outlive a short TTL. `tokenVersion` (or an equivalent live check) is the only approach that makes the change effective *immediately*, regardless of how long the token's own `exp` says it's still good for.

## Common Questions

**A user's role was changed in the admin panel, but they still have their old permissions until they log out and back in — why, and is that expected?**
> Yes, expected for a plain stateless-JWT setup: the role was a claim baked into their token at login, and nothing about changing the database record touches tokens that are already out in the world. See "Stale Claims" above — the `tokenVersion` pattern (or an equivalent live status check on the user record) is the standard fix if the change needs to take effect sooner than the token's natural expiry/refresh.

**Why include `aud` even when there's currently only one verifier?**
> Because the moment a second service starts accepting the same token issuer's tokens, `aud` is what stops a token minted for service A from being replayed against service B — cheap to add now, expensive to retrofit once tokens are already in production logs and caches.

**Is a JWT the right choice for a short-lived, narrow-purpose token (not a full login session)?**
> Yes — JWTs work well for exactly this, provided the claim shape reflects the narrower purpose (a distinct `token_use`/`typ`, a `scope` claim, a short `exp`) and, per the best practice above, doesn't share a verifier or signing key with a broader-privilege token class.

## Related

- [API Key](api-key.md) — the stateful alternative: opaque lookup token, instant revocation, no embedded claims
- [Access Token + Refresh Token Pattern](access-refresh-tokens.md) — how JWTs are used as short-lived access tokens paired with a long-lived, DB-backed refresh token for persistent sessions
- [JWT vs API Key](../../../overviews/security/jwt-vs-api-key.md) — when to choose each
- [Access Control & IAM](../authorization/access-control-iam.md)
- [OAuth Scopes & Least-Privilege Tokens](oauth-scopes.md)
- [Policy-Based Authorization](../../backend/data/policy-based-authorization.md)
- [Guards](../../backend/nestjs/guards.md)
- [HTTP Status Codes](../../backend/api/http-status-codes.md)
