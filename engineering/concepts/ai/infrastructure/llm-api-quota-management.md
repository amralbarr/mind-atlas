# LLM API Quota Management

An [LLM](../generation/llm.md) provider's capacity is constrained along **four distinct dimensions**, and a system that only manages one of them (usually just request count) is blind to the other three until something breaks:

| Dimension | What it measures | How to manage it |
|---|---|---|
| **Tokens per minute (TPM)** | Total input + output tokens processed per minute — the dimension that usually bites first for [RAG](../rag/rag.md), since a retrieved-context prompt can be thousands of tokens | Cap prompt and output tokens per request, and track a running token total against the limit before sending |
| **Requests per minute (RPM)** | Raw call count, independent of size | A standard [rate limiter](../../backend/architecture/rate-limiting.md) |
| **Concurrent requests** | How many calls are in flight at once — not every provider states this as an explicit published limit, but every provider has a practical ceiling | A semaphore bounding in-flight calls — see [the bounded-worker example](../../../code-samples/bounded-concurrent-worker/) for why a semaphore alone isn't sufficient without also bounding the queue feeding it |
| **Cost / spending budget** | Not a provider-enforced limit at all — a self-imposed ceiling the caller must track and enforce itself | Compute `tokens × price` per call, and aggregate that running cost per user, per tenant, and per day, independently of whether TPM/RPM/concurrency are anywhere near their limits |

See [Azure OpenAI](../../cloud/azure/azure-openai.md) for how the first two of these map directly onto a concrete provider's published quota model (TPM/RPM per deployment) — the four-dimension framework here is the general shape that applies to any [LLM](../generation/llm.md) provider, not just [Azure](../../cloud/azure/azure.md)'s.

## Different Request Types Need Different Limits

The design mistake is giving every request the same quota regardless of what it actually needs:

```
Chat message      →  small token cap    (a user is waiting; keep it fast and cheap)
RAG question       →  larger token cap   (retrieved context genuinely needs more tokens)
Background job      →  its own separate pool  (no one is waiting; shouldn't compete with live traffic at all)
```

This is the same high-priority/low-priority split already used for [bounding a traffic-spike queue by deadline](../../../interview/interview-01/07-python-api.md) — splitting concurrency slots between live chat and background jobs so a batch job can never starve a real user's request — applied one level up, to token *budget* per request type rather than just concurrency slots.

## Per-User and Per-Tenant Quotas

A global TPM/RPM/cost budget alone doesn't stop one misbehaving caller from consuming all of it — a stuck retry loop, a buggy client re-sending the same request, or one unusually heavy user can exhaust shared capacity for everyone else. The fix is layering quotas: a per-user or per-tenant cap *inside* the overall system limit, so one bad actor's consumption is bounded independently of how much headroom the system as a whole has left. This has a secondary benefit beyond fairness: a sudden spike in one specific user's or tenant's usage, tracked separately, is a much stronger signal of abuse or a bug than an aggregate system-wide spike is — the per-identity breakdown is what actually makes the anomaly visible instead of averaging it away.

## Alerting on Unusual Spikes

Because cost has no provider-side enforcement, it's the dimension most likely to go unnoticed until a bill arrives — which is why it needs its own explicit alerting, not just inclusion in a dashboard nobody checks proactively. A sudden spike in token usage, cost, or request rate *per user or tenant* — not just in aggregate — is the signal worth alerting on, since an aggregate-only view can hide a single bad actor inside otherwise-normal total traffic.

## Common Questions

**If TPM, RPM, and concurrency are all within limits, is cost automatically also under control?**
> No — cost is the one dimension with no provider-enforced ceiling at all. A system can run entirely within its TPM/RPM/concurrency limits while still spending far more than intended, if token volume per request is high enough; cost has to be tracked and alerted on independently, never inferred from the other three being healthy.

**Why track cost per user/tenant/day rather than just a single running total?**
> A single aggregate total tells you *that* spend is high, not *why* — per-user/tenant/day breakdown is what actually lets you find the specific caller or specific day responsible, and is also the natural unit for enforcing a per-tenant budget cap rather than only a system-wide one.

**Is a semaphore enough to bound concurrency safely?**
> Not by itself — a semaphore bounds how many tasks run *at once*, but if the tasks themselves are created in an unbounded loop before acquiring the semaphore, memory can still grow unbounded waiting to acquire it. A bounded queue feeding a fixed worker pool closes that gap; see the linked bounded-worker example for the concrete failure mode and fix.

## Related

- [Azure OpenAI](../../cloud/azure/azure-openai.md) — TPM/RPM as one concrete provider's instantiation of this general framework, plus provisioned throughput vs. pay-as-you-go
- [Rate Limiting](../../backend/architecture/rate-limiting.md) — the general RPM-style enforcement mechanism, and the `429`/`Retry-After` contract
- [Model Routing and Fallback](model-routing-and-fallback.md) — what to check before routing an over-quota request to a different, cheaper model instead of just queuing or rejecting it
- [Multi-Tenancy](../../backend/architecture/multi-tenancy.md) — the broader pattern per-tenant quotas are one instance of
- [Exponential Backoff and Jitter](../../backend/resilience/exponential-backoff-and-jitter.md) — required behavior once any of these four limits is actually hit
- [Q&A — Python, APIs & Practical Engineering](../../../interview/interview-01/07-python-api.md) — the worked numeric example deriving a priority-split queue limit from a deadline, the same chat-vs-background split this file generalizes to token budgets
