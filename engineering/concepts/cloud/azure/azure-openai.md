# Azure OpenAI Service

**Azure OpenAI** is Microsoft's managed offering of OpenAI's models (GPT, [embeddings](../../ai/ingestion/embeddings.md), etc.), delivered through [Azure](azure.md)'s identity, networking, and compliance wrapper rather than OpenAI's own API directly — the same underlying models, but with [Microsoft Entra ID](microsoft-entra-id.md) auth, [Azure RBAC](azure-rbac.md), private networking, and regional data-residency guarantees that calling OpenAI's public API doesn't provide. It's one of the [Azure AI services](azure-ai-services.md), and is commonly fronted by [Azure API Management](../../backend/api-gateways/azure-api-management.md) in an enterprise architecture rather than called directly by every client.

## Azure OpenAI (the Service) vs. Azure AI Foundry (the Platform)

These answer genuinely different questions, and the distinction is a common interview probe precisely because the names invite conflating them:

| | Azure OpenAI Service | [Azure AI Foundry](azure-ai-foundry.md) |
|---|---|---|
| **What it is** | One managed service — hosts OpenAI's models as **deployments**, each with its own TPM/RPM quota | A project/workspace platform that orchestrates Azure OpenAI *alongside* several other services into one application-building workflow |
| **Scope** | Narrow — inference endpoints for one model family | Broad — the catalog of open-source models, [Azure AI Search](azure-ai-search.md), prompt flow tooling, and evaluation frameworks, wired together in one workspace |
| **Consumption** | Call its [REST](../../backend/api/rest.md) API/SDK directly — no Foundry project required at all | A Foundry **project** bundles one or more Azure OpenAI deployments plus other resources under one workspace and portal |
| **Analogy** | The engine | The car — the chassis, wiring, and dashboard the engine gets assembled into |

Azure OpenAI is routinely used entirely standalone, with zero Foundry involvement — a team calling the Azure OpenAI [REST](../../backend/api/rest.md) API directly, managing its own deployments and quotas, is a complete and common architecture on its own. Foundry becomes the right layer specifically when a project needs a unified workspace spanning *more* than just Azure OpenAI — the open-source model catalog, [Azure AI Search](azure-ai-search.md) as a bundled retrieval layer, prompt flow, evaluation tooling — with Azure OpenAI's deployments as **one component** that workspace wires in, not an alternative Foundry replaces. This is the same shape as the already-documented [Azure AI services vs. Azure AI Foundry](azure-ai-services.md#azure-ai-services-vs-azure-ai-foundry) distinction: a task-specific service can be consumed standalone, or as a building block Foundry composes into a larger workspace.

## Quota Is Two-Dimensional: TPM and RPM

Every Azure OpenAI **deployment** (a named instance of a specific model version) has two independent quota limits, not one:

| Limit | Measures | Why it matters for [RAG](../../ai/rag/rag.md) specifically |
|---|---|---|
| **TPM** (Tokens Per Minute) | Total input + output tokens processed per minute | Usually the limit that bites **first** for [RAG](../../ai/rag/rag.md) workloads — a long retrieved-context prompt can be thousands of tokens per call, so a handful of concurrent [RAG](../../ai/rag/rag.md) requests can exhaust TPM long before RPM is a concern |
| **RPM** (Requests Per Minute) | Total number of calls per minute, regardless of size | The limit that matters more for short, high-frequency calls (classification, simple extraction) where each request is small |

This is distinct from the model's [context window](../../ai/generation/context-window.md) itself (the max tokens *one call* can process) — TPM/RPM is an *infrastructure* throttle on aggregate usage over time, the [context window](../../ai/generation/context-window.md) is an *architectural* ceiling per call; see [Context Window — vs. token limit vs. rate limit](../../ai/generation/context-window.md#context-window-vs-token-limit-vs-rate-limit) for the general three-way distinction this specializes.

**The practical consequence:** since TPM usually bites first for long RAG prompts, capping prompt and output tokens per request (trimming retrieved context to what's actually needed, setting a `max_tokens` ceiling on generation) directly protects TPM headroom — a cheap, high-leverage lever before reaching for more deployments or capacity.

## Handling a 429

A throttled request returns `429` with a `Retry-After` value (seconds to wait) — same mechanism as [Rate Limiting](../../backend/architecture/rate-limiting.md)'s general `429`/`Retry-After` contract, specialized to per-deployment TPM/RPM instead of a generic per-client limit. A well-behaved caller honors the provided `Retry-After` rather than computing its own backoff blindly, and still applies [jitter](../../backend/resilience/exponential-backoff-and-jitter.md) on top if multiple callers could be retrying at once.

## Scaling Beyond One Deployment

Once a single deployment's TPM/RPM ceiling is a real constraint (not just a request that needs to wait briefly), the next lever isn't "ask for a bigger limit" — it's spreading load across more deployments:

```
Client → Azure API Management (routes/load-balances) → Deployment A (East US)
                                                       → Deployment B (West Europe)
                                                       → Deployment C (East US, 2nd instance)
```

Deploying the same model across multiple regions or multiple deployments within a region, then load-balancing traffic across them from [Azure API Management](../../backend/api-gateways/azure-api-management.md) (or application-level routing logic), multiplies effective throughput — each deployment carries its own independent TPM/RPM quota. This also doubles as a resilience pattern: a throttled or degraded deployment can be routed around rather than becoming a single point of failure.

## Provisioned Throughput (PTU) vs. Pay-As-You-Go

| | Pay-as-you-go (consumption) | Provisioned Throughput (PTU) |
|---|---|---|
| **Billing** | Per token actually used | Reserved capacity, paid for whether fully utilized or not |
| **Latency/throughput** | Shared capacity — subject to noisy-neighbor variance | Dedicated, predictable latency and throughput |
| **Best for** | Variable, bursty, or overflow traffic | Predictable, high-priority, latency-sensitive production load |
| **Quota model** | TPM/RPM as described above | Throughput measured in PTUs, a separate dedicated-capacity unit |

The common production pattern combines both rather than choosing one: **provisioned throughput for the predictable baseline** (the traffic you know is coming and need consistent latency for), **pay-as-you-go for overflow** above that reserved capacity — the same reserved-capacity-plus-burst shape as autoscaling a fixed baseline of servers with elastic scale-out on top, applied to model inference capacity instead of compute instances.

## Common Questions

**If RPM looks fine but requests are still getting throttled, what should you check first?**
> TPM, not RPM — a RAG workload's bottleneck is overwhelmingly more likely to be token volume (long prompts with substantial retrieved context) than raw request count. Checking RPM alone and concluding "we have headroom" while TPM is actually exhausted is a common, avoidable misdiagnosis.

**Does provisioned throughput eliminate the need for retry/backoff logic?**
> No — PTU reduces the *likelihood* of throttling for the reserved baseline, but any capacity model can still be exhausted under an unexpected spike, and a PTU deployment can still fail for other transient reasons (network issues, a regional incident). [Exponential backoff and jitter](../../backend/resilience/exponential-backoff-and-jitter.md) remains necessary regardless of which billing/capacity model is in use.

**Is spreading traffic across regions purely a throughput play, or does it affect data residency?**
> It can affect both, and the two considerations can conflict — a deployment in a different region may have different data-residency implications for the data sent to it. Multi-region scaling for throughput has to be validated against whatever data-residency and compliance constraints apply to the content being sent, not treated as a purely capacity-driven decision.

## Related

- [Azure AI Foundry](azure-ai-foundry.md) — the project/workspace platform that orchestrates Azure OpenAI alongside other services, as distinguished above
- [Azure AI Services](azure-ai-services.md) — the broader family of managed AI APIs Azure OpenAI is one member of
- [Azure API Management](../../backend/api-gateways/azure-api-management.md) — the gateway commonly fronting multi-deployment Azure OpenAI setups for routing, [rate limiting](../../backend/architecture/rate-limiting.md), and centralized auth
- [Rate Limiting](../../backend/architecture/rate-limiting.md) — the general `429`/`Retry-After` contract this file's TPM/RPM throttling specializes
- [Exponential Backoff and Jitter](../../backend/resilience/exponential-backoff-and-jitter.md) — required client-side behavior regardless of PTU vs. pay-as-you-go
- [Context Window](../../ai/generation/context-window.md) — the per-call architectural limit, distinct from TPM/RPM's per-minute infrastructure limit
- [Microsoft Entra ID](microsoft-entra-id.md) / [Azure RBAC](azure-rbac.md) — the identity and access layer Azure OpenAI adds on top of the underlying OpenAI models
