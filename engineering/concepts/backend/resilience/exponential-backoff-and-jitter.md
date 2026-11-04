# Exponential Backoff and Jitter

**Exponential backoff** is a retry strategy where the wait time before each retry attempt grows exponentially instead of staying fixed — attempt 1 waits a short delay, attempt 2 waits roughly double that, attempt 3 double again, up to a capped maximum. **Jitter** adds randomness to that delay so that many clients failing at the same moment don't all retry at exactly the same instant. The two are almost always used together: backoff alone still produces a synchronized herd of retries; jitter alone doesn't grow the delay as failures persist.

## Why Backoff Alone Isn't Enough

```
Without backoff: retry immediately, every 100ms
  → a struggling downstream service gets hammered harder while it's already failing

With fixed backoff: retry every 2s
  → better, but if 1,000 clients all failed at the same second (e.g. the
    dependency just went down), they all retry at the same 2s mark again —
    a synchronized spike, not a smooth recovery

Exponential backoff + jitter: retry at a randomized delay that grows each attempt
  → load spreads out over time instead of re-synchronizing on every retry
```

This synchronized-retry failure mode is called a **thundering herd** — the exact problem jitter exists to prevent.

## The Formula

```
delay = min(max_delay, base_delay * 2^attempt)
```

| Attempt | `base_delay = 200ms` |
|---|---|
| 1 | 200ms |
| 2 | 400ms |
| 3 | 800ms |
| 4 | 1,600ms |
| 5 | 3,200ms (capped at `max_delay`, e.g. 2,000ms → stays at 2,000ms) |

A `max_delay` cap is essential — uncapped exponential growth turns a brief outage into a multi-minute wait by attempt 6 or 7.

## Jitter Strategies

| Strategy | Formula | Behavior |
|---|---|---|
| **No jitter** | `delay = base * 2^attempt` | Synchronized retries — the thundering-herd problem |
| **Full jitter** | `delay = random(0, base * 2^attempt)` | Delay is uniformly random between 0 and the capped exponential value — spreads load the most, but some retries fire almost immediately |
| **Equal jitter** | `delay = (base * 2^attempt) / 2 + random(0, (base * 2^attempt) / 2)` | Never faster than half the computed delay, still randomized — a middle ground when firing too early is undesirable |
| **Decorrelated jitter** | `delay = min(max_delay, random(base, previous_delay * 3))` | Each client's sequence of delays is decorrelated from every other client's, not just randomized once — generally the best spread under high contention |

**Full jitter** is the simplest and most commonly implemented; it's the default most [HTTP](../../networking/http.md) client retry libraries ship with. The canonical reference is [AWS](../../cloud/infrastructure/aws.md)'s "Exponential Backoff And Jitter" architecture blog post, which benchmarked all four strategies above.

## Which Failures to Retry

Retrying is only safe — and only helps — for **transient** failures:

| Retry | Example | Why |
|---|---|---|
| ✅ Yes | `503 Service Unavailable`, `429 Too Many Requests`, connection reset, [DNS](../../networking/dns.md) timeout | Temporary — a second attempt has a real chance of succeeding |
| ❌ No | `400 Bad Request`, `403 Forbidden`, `404 Not Found` | The request itself is wrong or disallowed — retrying produces the exact same failure every time, wasting a call for nothing |

See [HTTP Status Codes](../api/http-status-codes.md) for the full 4xx/5xx breakdown, and [Rate Limiting](../architecture/rate-limiting.md) for how a well-behaved client should honor a server's `Retry-After` header on `429`/`503` instead of computing its own backoff blindly — the server is telling you exactly how long to wait, which takes priority over a guessed delay.

## Code Example (Python)

```python
import random
import time

def call_with_backoff(fn, max_attempts=4, base_delay=0.2, max_delay=2.0):
    for attempt in range(max_attempts):
        try:
            return fn()
        except TransientError:
            if attempt == max_attempts - 1:
                raise
            capped = min(max_delay, base_delay * 2 ** attempt)
            delay = random.uniform(0, capped)   # full jitter
            time.sleep(delay)
    raise RuntimeError("unreachable")
```

`TransientError` here represents only the retryable failure classes above — a `PermissionError` or a validation error should never reach this loop; it should fail immediately.

## Retry Budgets and Single-Layer Retry

A retry budget caps the *total* number of attempts across a request's whole lifetime, not just per call — without one, a request that fans out to several dependencies can multiply into dozens of actual network calls. The related, often-missed rule: **only one layer in a call chain should retry.** If a frontend, an API gateway, and the backend service each independently retry three times, a single transient failure turns into up to 27 real attempts hitting an already-struggling dependency — exactly when it can least afford the extra load. Decide which single layer owns retry responsibility for a given call, and have every other layer propagate the failure instead of retrying it again.

## Interaction With Deadlines and Idempotency

Backoff delay has to fit inside the request's own end-to-end deadline — see [Throughput and Latency](../architecture/throughput-and-latency.md#percentile-latency--p50-p95-p99) for sizing that deadline off P95/P99 latency rather than the average case, and bounding it below whatever a load balancer or gateway will itself wait before returning a [504 Gateway Timeout](../api/http-status-codes.md). Retrying a side-effecting operation (a payment, a booking) also requires an [idempotency key](../api/idempotency.md) that stays identical across every retry of that same operation, so a retried write can't be applied twice.

## Common Questions

**Isn't jitter just adding noise — why does randomness help?**
> Because the failure that triggered the retry was itself synchronized across clients (a shared dependency went down for everyone at once). Without jitter, every client's deterministic backoff schedule stays synchronized too, so they all retry together on every attempt. Randomizing each client's delay breaks that synchronization, spreading the retry load smoothly over time instead of in repeated spikes.

**How is this different from a circuit breaker?**
> They solve different problems and are normally combined: backoff-with-jitter handles *how* a single client retries one transient failure; a circuit breaker handles *whether* to keep trying at all after repeated failures, by failing fast for a cooldown period instead of continuing to retry against a dependency that's clearly down. See [Resilience4j](resilience4j.md) for a library implementing both together.

## Related

- [Resilience4j](resilience4j.md) / [Hystrix](hystrix.md) / [Polly](polly.md) — libraries implementing retry-with-backoff alongside circuit breakers, timeouts, and bulkheads
- [Rate Limiting](../architecture/rate-limiting.md) — the `429`/`Retry-After` contract a well-behaved retrying client must honor
- [HTTP Status Codes](../api/http-status-codes.md) — the transient (`429`/`503`/`504`) vs. non-retryable (`400`/`403`/`404`) status codes this pattern depends on distinguishing
- [Idempotency](../api/idempotency.md) — required before retrying any side-effecting operation
- [Throughput and Latency](../architecture/throughput-and-latency.md) — P95/P99 as the basis for sizing the deadline backoff delays must fit inside
- [Load Balancing](../../networking/load-balancing.md) — a load balancer's own upstream timeout is a hard ceiling an application-level deadline must stay under
- [Dead Letter Queue](../../distributed-systems/messaging/dead-letter-queue.md) — where a message goes after retries are exhausted
- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md#resilience-patterns) — retry-with-backoff alongside the other resilience patterns (circuit breaker, timeout, bulkhead)
