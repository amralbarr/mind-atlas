# Lakera Guard

**Lakera Guard** is a third-party, cloud- and model-agnostic API for detecting [prompt injection](prompt-injection.md), jailbreak attempts, and other [LLM](../../ai/generation/llm.md)-specific threats in real time — a dedicated "[LLM](../../ai/generation/llm.md) firewall" that sits in front of (and optionally behind) a model call, rather than a feature bundled into any one cloud provider's AI platform.

## What It Screens

| Category | Example |
|---|---|
| **[Prompt injection](prompt-injection.md) / jailbreak** | "Ignore your previous instructions," known jailbreak phrasing patterns, instructions hidden inside retrieved/third-party content |
| **PII leakage** | Detects personally identifiable information appearing in a prompt or a model's output before it's exposed |
| **Unknown/malicious links** | Flags URLs in model input or output that could be used for phishing or SSRF-style exfiltration |
| **Content moderation** | General unwanted/harmful content, similar in spirit to [Azure AI Content Safety](azure-prompt-shields.md)'s broader moderation scope |

The injection/jailbreak category is the one most directly comparable to [Azure Prompt Shields](azure-prompt-shields.md) — both exist to answer the same question (does this content try to override the model's instructions?), just as independently swappable classification calls.

## How It's Used

```
User message  (and/or retrieved documents, tool output)
         │
         ▼
Lakera Guard API call  →  { flagged: true/false, category breakdown }
         │
         ▼
If flagged: block, log, and return a safe response
         │
         ▼
If clean: proceed to the LLM call as normal
```

Because it's a plain [HTTP](../../networking/http.md) API independent of any specific model provider, the same integration works unchanged whether the application calls OpenAI, Anthropic, a self-hosted model via [vLLM](../../ai/infrastructure/vllm.md), or anything else — a relevant distinction for a multi-model or multi-cloud system where a provider-specific tool like [Azure Prompt Shields](azure-prompt-shields.md) would only cover [Azure](../../cloud/azure/azure.md)-side deployments.

## What It Is Not

Like any classifier-based detection layer, Lakera Guard is probabilistic — it will have both false positives (blocking legitimate content) and false negatives (missing a real attack). It is explicitly a belt-and-suspenders layer on top of architectural defenses, never a replacement for the [query-time access-control filter upstream of retrieval](prompt-injection.md#the-full-defense-pipeline), which remains the strongest defense because it doesn't depend on any detector — or the model — behaving correctly.

## Lakera Guard vs. Azure Prompt Shields

See the comparison table in [Azure Prompt Shields](azure-prompt-shields.md#azure-prompt-shields-vs-lakera-guard) — the short version is: Lakera Guard is the vendor-neutral choice when the system isn't exclusively built on [Azure AI Services](../../cloud/azure/azure-ai-services.md), since it works the same way regardless of which model or cloud serves the actual request.

## Common Questions

**Does Lakera Guard replace the need for output filtering?**
> No — it complements rather than replaces [output filtering](prompt-injection.md#additional-defenses). Lakera Guard can screen both input and output, but a system should still validate the final answer against its own rules (e.g. checking that cited sources actually exist, as covered elsewhere in [RAG](../../ai/rag/rag.md) evaluation) rather than treating a "clean" Guard verdict as proof the answer is correct or safe.

**Why would a team pick a third-party detector instead of their cloud provider's built-in one?**
> Model/cloud independence is the main reason — a team running models across multiple providers or planning to switch providers later gets one consistent detection layer that doesn't need to be re-integrated per provider, unlike a cloud-native feature tied to that one platform.

## Related

- [Prompt Injection](prompt-injection.md) — the attack class this tool detects, including the full defense pipeline it's one layer of
- [Azure Prompt Shields](azure-prompt-shields.md) — the [Azure](../../cloud/azure/azure.md)-native equivalent, bundled into [Azure AI Content Safety](azure-prompt-shields.md)
- [RAG](../../ai/rag/rag.md) — the pattern that introduces the third-party/grounding content this tool can screen
- [Tool Calling](../../ai/agents/tool-calling.md) — tool output is another indirect-attack surface this detector can screen
