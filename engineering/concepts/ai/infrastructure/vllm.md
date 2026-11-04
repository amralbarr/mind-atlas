# vLLM

vLLM is an open-source, high-throughput inference server for serving [LLMs](../generation/llm.md) — the self-hosted alternative to a managed endpoint like [Azure](../../cloud/azure/azure.md) OpenAI. It's the production inference layer behind this handbook's own reference [RAG](../rag/rag.md) stack (vLLM + pgvector + [OpenTelemetry](../../backend/observability/opentelemetry.md)), referenced throughout as the "self-hosted" side of every managed-vs-self-hosted inference trade-off.

## What it actually does

vLLM takes an open-weight model (Llama, Mistral, Qwen, and others via HuggingFace) and serves it behind an OpenAI-compatible [HTTP](../../networking/http.md) API, optimized specifically for throughput under concurrent load:

- **Continuous batching** — incoming requests are queued and processed together on the GPU rather than one at a time, dramatically increasing token throughput at the cost of slightly higher latency for the first request in a batch. This is the core trade-off vLLM makes: optimize for GPU utilization (tokens/sec across many users) over the absolute fastest single-request latency.
- **PagedAttention** — vLLM's memory-management technique for the KV cache (the per-request attention memory that grows as a generation proceeds), which lets it pack far more concurrent requests into the same GPU memory than a naive implementation.
- **OpenAI-compatible API** — a vLLM server can usually be swapped in wherever code expects the OpenAI API shape, which is why it's a common drop-in self-hosted replacement for a managed endpoint.
- **Multi-[LoRA](lora.md) serving** — vLLM can load one frozen base model and serve several [LoRA](lora.md) adapters concurrently against it, picking the right adapter per request, instead of needing a fully separate deployed model per fine-tuned task.

## Why choose vLLM over a managed endpoint (and vice versa)

| | Self-hosted vLLM | Managed endpoint (e.g. [Azure](../../cloud/azure/azure.md) OpenAI) |
|---|---|---|
| **Data residency** | Full control — nothing leaves your infrastructure | Data processed by the provider, subject to their terms |
| **Cost at scale** | Pay for GPU compute directly — cheaper at sustained high volume | Pay per token — simpler, but costs scale linearly with usage forever |
| **Model choice** | Any open-weight model (Llama, Mistral, Qwen, fine-tuned variants) | Whatever the provider offers |
| **Operational burden** | You own GPU provisioning, scaling, patching, uptime | Provider's responsibility |
| **Time to first deployment** | Slower — infrastructure to stand up first | Fastest — an [API key](../../security/auth/api-key.md) and you're serving traffic |

The practical decision rule: self-host if data cannot leave the organization or cost at sustained scale matters enough to justify the ops burden; use a managed endpoint when speed to market and zero infrastructure ownership matter more.

## Related

- [Pilot and Delivery Patterns](pilot-and-delivery-patterns.md) — the self-hosted-vs-managed inference decision in context
- [Azure AI Foundry](../../cloud/azure/azure-ai-foundry.md) — [Azure](../../cloud/azure/azure.md) OpenAI Service, the managed-endpoint alternative vLLM is most often compared against
- [Throughput and Latency](../../backend/architecture/throughput-and-latency.md) — the batching/throughput trade-off vLLM is built around
- [OpenTelemetry](../../backend/observability/opentelemetry.md) — tracing an `llm_generate` span through a vLLM-backed pipeline
- [LoRA](lora.md) — the [fine-tuning](fine-tuning.md) technique vLLM's multi-adapter serving is built around
- [RAG](../rag/rag.md)
