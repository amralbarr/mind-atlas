# HTTP Status Codes

A three-digit code returned with every [HTTP](../../networking/http.md) response, telling the client broadly what happened without it having to parse the response body. The first digit indicates the **class**; the other two narrow it down.

## The Five Classes

| Range | Class | Meaning |
|---|---|---|
| **1xx** | Informational | Request received, still processing — rarely handled explicitly by application code |
| **2xx** | Success | The request was received, understood, and accepted |
| **3xx** | Redirection | Further action needed to complete the request (usually follow a different URL) |
| **4xx** | Client Error | The request is invalid, unauthorized, or otherwise the client's fault |
| **5xx** | Server Error | The server failed to fulfill a valid request — the client's fault to retry, not to fix |

## 2xx — Success

| Code | Name | Typical use |
|---|---|---|
| `200` | OK | Standard success response, body contains the result |
| `201` | Created | A new resource was created (typically after `POST`); often includes a `Location` header pointing to it |
| `202` | Accepted | Request accepted for processing, but not completed yet (async/queued work) |
| `204` | No Content | Success, but there's deliberately no response body (common after `DELETE` or some `PUT` updates) |

## 3xx — Redirection

| Code | Name | Typical use |
|---|---|---|
| `301` | Moved Permanently | Resource has a new permanent URL — clients/search engines should update references |
| `302` | Found | Temporary redirect — the original URL should still be used for future requests |
| `304` | Not Modified | Client's cached copy is still valid (used with conditional requests / `ETag`) |

## 4xx — Client Error

| Code | Name | Typical use |
|---|---|---|
| `400` | Bad Request | Malformed request — invalid syntax, failed validation, missing required fields |
| `401` | Unauthorized | **[Authentication](../../security/auth/authentication.md)** failed or missing — the server doesn't know who you are (misleadingly named; "Unauthenticated" would be more accurate) |
| `403` | Forbidden | **[Authorization](../../security/authorization/authorization.md)** failed — the server knows exactly who you are, and you're not allowed to do this |
| `404` | Not Found | No resource exists at this URL (also commonly used to hide the *existence* of a resource from unauthorized callers — see below) |
| `405` | Method Not Allowed | The URL exists, but doesn't support this [HTTP](../../networking/http.md) method (e.g. `DELETE` on a read-only endpoint) |
| `409` | Conflict | The request conflicts with the current state of the resource (e.g. a unique-constraint violation, an edit based on stale data) |
| `422` | Unprocessable Entity | Syntactically valid request, but semantically invalid (e.g. valid [JSON](../../programming/fundamentals/json.md) that fails business-rule validation) |
| `429` | Too Many Requests | Rate limit exceeded — should be paired with a `Retry-After` header |

## 5xx — Server Error

| Code | Name | Typical use |
|---|---|---|
| `500` | Internal Server Error | Generic catch-all — something broke, and it's not the client's fault |
| `502` | Bad Gateway | A [reverse proxy](../../networking/reverse-proxy.md)/gateway got an invalid response from an upstream server |
| `503` | Service Unavailable | Server temporarily can't handle the request (overload, maintenance) — often paired with `Retry-After` |
| `504` | Gateway Timeout | A [reverse proxy](../../networking/reverse-proxy.md)/gateway didn't get a response from upstream in time |

## The Classic Confusion: 401 vs. 403

This is the single most commonly mixed-up pair in the entire status code list, because both describe some flavor of "you can't do that" — but they answer different questions:

| | `401 Unauthorized` | `403 Forbidden` |
|---|---|---|
| Question it answers | **Who are you?** (identity unknown/unproven) | **Are you allowed?** (identity known, permission denied) |
| Typical cause | Missing, expired, or invalid credentials/token | Valid credentials, but insufficient role/permission/scope |
| Correct client reaction | Re-authenticate (log in again, refresh the token) | Don't retry with the same credentials — nothing about re-authenticating fixes this |
| Required response header | Must include a `WWW-Authenticate` header per the [HTTP](../../networking/http.md) spec (often omitted in practice by APIs that aren't using [HTTP](../../networking/http.md)'s native auth challenge) | No equivalent required header |

A concrete example that separates them cleanly: a request with no token at all, or an expired one, is `401`. A request with a perfectly valid, current token belonging to a regular user trying to hit an admin-only endpoint is `403` — the server has no doubt who's asking, it just says no.

**A common intentional exception**: some APIs return `404 Not Found` instead of `403` when the mere existence of a resource is itself sensitive information (e.g. someone else's private document at a guessable URL) — returning `403` confirms "yes, this exists, you're just not allowed to see it," while `404` reveals nothing. This is a deliberate information-disclosure trade-off, not a mistake.

## Common Questions

**A user's permissions changed, but requests still return success where they should now fail — is that a status-code bug?**
> Not directly — that's usually the underlying [authorization](../../security/authorization/authorization.md) check still passing because of stale data, not a wrong status code being chosen. See [Stale Claims](../../security/auth/jwt.md#stale-claims-a-different-problem-from-revocation) for the [JWT](../../security/auth/jwt.md)-specific version of this: a token can carry an old role that no code path re-checks until the token naturally expires.

**Should validation failures return `400` or `422`?**
> Convention varies — `400` for structurally malformed requests (bad [JSON](../../programming/fundamentals/json.md), wrong types) and `422` for well-formed requests that fail business-level validation (a valid-looking email that's already taken) is a common split, but plenty of APIs use `400` for both. Consistency within one API matters more than which specific convention is chosen.

**Why does `401` sound like it should mean "not authorized" when it's actually about [authentication](../../security/auth/authentication.md)?**
> A historical naming inconsistency in the original [HTTP](../../networking/http.md) spec — the header required alongside it, `WWW-Authenticate`, points at the intended meaning ([authentication](../../security/auth/authentication.md), not [authorization](../../security/authorization/authorization.md)) more clearly than the status name itself does.

## Related

- [REST](rest.md)
- [JWT](../../security/auth/jwt.md)
- [Guards](../nestjs/guards.md)
- [Access Control & IAM](../../security/authorization/access-control-iam.md)
- [OAuth Scopes & Least-Privilege Tokens](../../security/auth/oauth-scopes.md)
- [HTTP](../../networking/http.md)
- [Exponential Backoff and Jitter](../resilience/exponential-backoff-and-jitter.md) — which of these codes (`429`/`503`/`504`) are safe to retry vs. never (`400`/`403`/`404`)
