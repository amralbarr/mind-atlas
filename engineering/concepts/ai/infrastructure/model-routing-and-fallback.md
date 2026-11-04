# Model Routing and Fallback

**Model routing** is sending different requests to different models based on cost, capability, or availability, rather than every call going to one fixed model. **Fallback** is the specific, reactive case: the primary model is throttled, down, or degraded, so the system automatically substitutes an alternate — usually cheaper or more available, rarely equivalent in every respect. Routing is a deliberate design choice made ahead of time; fallback is a safety behavior that activates under failure, and the second is considerably riskier because it happens automatically, under pressure, with less opportunity for a human to catch something wrong before it ships to a user.

## The Checklist Before Allowing an Automatic Fallback

Falling back to a different, cheaper model is not just "same request, cheaper bill" — it changes the actual behavior a user receives, often silently. Before a fallback path is allowed to fire automatically:

| Check | What can go wrong if skipped |
|---|---|
| **Data residency / privacy** | A fallback model hosted in a different region, or by a different provider entirely, can carry different data-handling guarantees than the primary — sending the same request there can violate a compliance or contractual commitment the primary model satisfied |
| **Safety / content-moderation parity** | A different model may have different (often weaker, sometimes just *different*) content filtering — a request that was safely handled by the primary's guardrails isn't guaranteed to be handled the same way by the fallback |
| **Capability parity** | The fallback must actually support what the request needs — function/[tool calling](../agents/tool-calling.md), [structured output](../generation/structured-output.md)/[JSON](../../programming/fundamentals/json.md) mode, the same [context window](../generation/context-window.md) size for a long prompt. A silent capability gap doesn't fail loudly; it just produces a worse or malformed response |
| **Quality validation** | "It responds" is not "it responds *well enough for this task*" — the fallback model needs its own evaluation on a representative task sample, not an assumption that any model answering the same prompt format produces comparable quality. See [Groundedness and Correctness](../evaluation/groundedness-and-correctness.md) and [LLM Evaluation](../evaluation/llm-evaluation.md) for what "validated" should actually mean here, not just a spot-check |
| **Prompt/format compatibility** | The same literal prompt can behave differently across model families — a [system prompt](../generation/system-prompt.md) tuned for one model's instruction-following style doesn't automatically transfer; verify the fallback actually follows the same instructions acceptably, not just that it accepts the same input format |
| **Cost and latency delta being an accepted trade-off** | A cheaper fallback is usually cheaper *because* it's smaller/slower/less capable — that trade-off should be a decision the product has consciously accepted for the fallback scenario, not a side effect nobody signed off on |
| **Logging and visibility** | Every fallback activation should be logged and distinguishable from normal operation — silent fallback makes a quality regression invisible until a user complains, with no signal pointing at the actual cause |

Skipping any of these turns "we have a resilience feature" into "we silently degraded what customers receive, and may not even know it's happening."

## Routing Strategies, More Broadly

Fallback is the narrowest, most reactive case of a broader pattern:

| Strategy | Basis for the routing decision | Example |
|---|---|---|
| **Task-based routing** | Route by what the request actually needs | A simple classification task goes to a small, cheap model; a complex multi-step reasoning task goes to a larger one |
| **Cost-tiered routing** | Route by budget/priority of the caller or workload | A background batch job uses a cheaper model; a live, user-facing chat uses the higher-quality one — the same priority split already used for queue/capacity allocation during a traffic spike |
| **Availability-based fallback** | Route by whether the primary is currently reachable/under quota | The case this file's checklist above addresses directly |
| **Multi-provider routing** | Route across different model providers entirely, not just different deployments of one provider | Reduces single-provider dependency, at the cost of needing the above checklist validated per provider, not just per model |

All four share the same underlying requirement: whatever target a request can be routed to must already be validated for that request's actual needs — routing logic that's purely cost- or availability-aware, with no awareness of capability/quality/compliance fit, is a liability wearing a cost-optimization feature's clothing.

## Common Questions

**Should fallback ever happen without any human visibility into when it's firing?**
> No — even a fully automatic fallback path needs logging/alerting on activation, and ideally a dashboard showing fallback rate over time. A fallback that fires silently and successfully from an uptime perspective can still be a quality regression that nobody notices until a user complaint surfaces it, by which point it may have been running for a while.

**Is it acceptable to validate the fallback model once and trust it indefinitely?**
> No — model versions change (a provider updates a model behind the same name/endpoint), and the request mix a system actually sends changes over time too. The validation that justified an automatic fallback needs periodic re-confirmation against current traffic patterns and the current model version, the same discipline [LLM Evaluation](../evaluation/llm-evaluation.md) applies to any model version change generally.

**Does [Azure OpenAI](../../cloud/azure/azure-openai.md)'s multi-deployment/multi-region scaling count as "fallback" in this sense?**
> Only partially — spreading load across multiple deployments of the *same* model version, as covered in [Azure OpenAI](../../cloud/azure/azure-openai.md#scaling-beyond-one-deployment), avoids most of this checklist because the target is identical in capability/safety/quality to the primary; it's a throughput/availability play, not a model-substitution one. The checklist above applies specifically when the *model itself* changes, not just which deployment of the same model serves the request.

## Related

- [Azure OpenAI](../../cloud/azure/azure-openai.md) — the concrete platform context (TPM/RPM throttling, provisioned throughput vs. pay-as-you-go) that often triggers a fallback decision in the first place
- [Groundedness and Correctness](../evaluation/groundedness-and-correctness.md) / [LLM Evaluation](../evaluation/llm-evaluation.md) — what "quality validated" actually requires, beyond a spot-check
- [Structured Output](../generation/structured-output.md) — a capability-parity check a fallback model must specifically satisfy if the primary relies on it
- [Context Window](../generation/context-window.md) — another capability dimension that can differ silently between a primary and fallback model
- [Exponential Backoff and Jitter](../../backend/resilience/exponential-backoff-and-jitter.md) — the retry behavior that should be exhausted on the primary before falling back, not a substitute for it
- [Rate Limiting](../../backend/architecture/rate-limiting.md) — the throttling signal that most commonly triggers an availability-based fallback decision
