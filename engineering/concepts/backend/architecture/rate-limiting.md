# Rate Limiting

Rate limiting caps how many requests a client (a user, an [API key](../../security/auth/api-key.md), an IP address) can make within a given time window, rejecting or delaying anything past that threshold. It protects a system from being overwhelmed — by a genuine traffic spike, a buggy retry loop, or a deliberate abuse/brute-force attempt — and keeps capacity fair across many clients.

## Why It's Needed

Without rate limiting, a single misbehaving client (or attacker) can consume disproportionate resources, degrading service for everyone else, or amplify a [brute-force](../../security/attacks/brute-force.md) attack against a login endpoint into thousands of attempts per second. Rate limiting is one of the cheapest, highest-leverage protections a backend can add.

## The Core Algorithms

| Algorithm | How it works | Trade-off |
|---|---|---|
| **Fixed window** | Count requests in the current wall-clock window (e.g. per calendar minute); reset to zero when the window rolls over | Simple, but allows a burst of `2×limit` right at a window boundary (max requests at the end of one window + max at the start of the next) |
| **Sliding window** | Counts requests in a rolling window that moves continuously with time, rather than resetting at fixed boundaries | Smooths out the boundary-burst problem; more accurate, slightly more expensive to compute |
| **Token bucket** | A bucket holds tokens, refilled at a steady rate up to a cap; each request consumes one token; empty bucket = request rejected | Naturally allows short bursts (up to the bucket size) while enforcing a steady average rate — the most common real-world choice |
| **Leaky bucket** | Requests queue into a bucket that "leaks" (processes) at a fixed rate; if the bucket overflows, new requests are dropped | Smooths bursts into a perfectly steady output rate — good for protecting a downstream system that truly can't handle spikes at all |

### Token Bucket, Visually

```text
Bucket capacity: 10 tokens, refill rate: 5 tokens/sec

t=0:  [██████████] 10 tokens — burst of 10 requests allowed instantly
t=0:  request arrives → consumes 1 token → [█████████ ] 9 left
...
t=1s: +5 tokens refilled (capped at 10)
```

A token bucket is popular precisely because real traffic isn't perfectly smooth — it allows a reasonable burst (a user rapid-clicking a button) while still enforcing a hard average rate over time, unlike a strict fixed window that either allows or blocks with no nuance about burst shape.

## Implementing Fixed-Window Counting (Redis)

```javascript
async function isAllowed(userId, limit = 100, windowSeconds = 60) {
  const key = `ratelimit:${userId}:${Math.floor(Date.now() / 1000 / windowSeconds)}`;
  const count = await redis.incr(key);
  if (count === 1) await redis.expire(key, windowSeconds);
  return count <= limit;
}
```

Redis is a natural fit for distributed rate limiting because the counter needs to be shared across every server instance handling requests — an in-memory counter on a single server is meaningless the moment traffic is load-balanced across multiple instances.

## What to Rate Limit By

| Key | Use case |
|---|---|
| **[API key](../../security/auth/api-key.md) / user ID** | Per-customer quotas on a public API (e.g. "1000 requests/day on the free tier") |
| **IP address** | Protecting anonymous/unauthenticated endpoints like login or signup from abuse |
| **Endpoint** | Some routes (search, AI inference) are far more expensive per call and deserve a tighter limit than a cheap `GET /health` |
| **Global** | An overall cap protecting a downstream dependency (e.g. a third-party API with its own rate limits) regardless of which internal caller is making the request |

## Signaling Limits to Clients

A well-designed API tells the client where it stands instead of just returning an opaque failure:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1699999999
Retry-After: 42
```

`429 Too Many Requests` is the standard [HTTP status code](../api/http-status-codes.md) for this; `Retry-After` tells a well-behaved client exactly how long to back off before retrying, rather than guessing or hammering the endpoint immediately again.

## Where Rate Limiting Lives in the Stack

Rate limiting can be enforced at multiple layers, and real systems often combine them:

| Layer | Example |
|---|---|
| **[Reverse proxy](../../networking/reverse-proxy.md) / API gateway** | [NGINX](../api-gateways/nginx.md)'s `limit_req_zone`, [Kong](../api-gateways/kong.md) rate-limiting plugin, [AWS API Gateway](../api-gateways/aws-api-gateway.md) usage plans — stops abusive traffic before it even reaches application code |
| **Application [middleware](../middleware.md)** | `@nestjs/throttler`, Express `express-rate-limit` — useful when limits need to vary per authenticated user/plan, which the gateway layer may not have visibility into |
| **Client-side (self-imposed)** | A well-behaved API client throttles its own outgoing calls to stay under a third-party API's published limits, avoiding ever hitting a `429` in the first place |

## Rate Limiting vs. Throttling vs. Backpressure

These three are related but distinct: rate limiting **rejects** requests past a threshold outright; throttling can mean the same thing or can mean deliberately **slowing** processing rather than rejecting; [backpressure](../../distributed-systems/patterns/backpressure.md) is a broader concept about a system signaling upstream "slow down" when it can't keep up, which rate limiting is one specific, client-facing mechanism for enforcing.

## Common Questions

**Why is token bucket more popular than fixed window in production systems?**
> Because fixed window allows a burst of nearly double the intended limit right at a window boundary, while token bucket enforces a true steady-state average rate while still tolerating short, reasonable bursts — a better match for how real traffic actually behaves.

**Does rate limiting protect against DDoS attacks?**
> Only partially — rate limiting per client/IP helps against abuse from a *known, identifiable* source, but a distributed attack spreading requests across thousands of IPs can still overwhelm a system even with per-IP limits in place. DDoS mitigation typically needs additional infrastructure (a [CDN](../../networking/cdn.md)/scrubbing service) upstream of application-level rate limiting.

**Should rate limits be enforced at the gateway or in application code?**
> Ideally both, for different reasons: the gateway/proxy layer stops obviously abusive traffic cheaply before it consumes application resources at all, while application-level limiting can apply business-specific rules (different limits per subscription tier) that the gateway may not have the context to enforce.

## Related

- [NGINX](../api-gateways/nginx.md)
- [Kong](../api-gateways/kong.md)
- [Brute Force](../../security/attacks/brute-force.md)
- [Backpressure](../../distributed-systems/patterns/backpressure.md)
- [HTTP Status Codes](../api/http-status-codes.md)
- [Exponential Backoff and Jitter](../resilience/exponential-backoff-and-jitter.md) — how a well-behaved client should respond to a `429`'s `Retry-After` header
- [LLM API Quota Management](../../ai/infrastructure/llm-api-quota-management.md) — RPM as one of four quota dimensions an [LLM](../../ai/generation/llm.md) API caller must manage, alongside TPM, concurrency, and cost
- [Azure API Management](../api-gateways/azure-api-management.md) — a managed gateway implementing rate limiting declaratively via policy, rather than application [middleware](../middleware.md)
