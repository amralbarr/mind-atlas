# Fine-tuning

## What is it?

Fine-tuning is the process of continuing to train an already-trained (pretrained) [LLM](../generation/llm.md) on a smaller, task-specific dataset, adjusting the model's own weights so its behavior changes permanently for that use case. This is different from every other technique for steering an [LLM](../generation/llm.md)'s output — [prompt engineering](../generation/prompt-engineering.md) and [RAG](../rag/rag.md) both leave the model's weights untouched and instead change what the model *sees* at request time; fine-tuning changes what the model *is*.

```
Pretrained base model (trained on general internet-scale text)
         ↓
+ Fine-tuning dataset (hundreds to thousands of task-specific examples)
         ↓
Fine-tuned model (same architecture, adjusted weights,
                  specialized behavior baked in)
```

## Fine-tuning vs. RAG vs. prompt engineering

This is one of the most common points of confusion in [LLM](../generation/llm.md) engineering, because all three sound like "make the model do X better" but they solve genuinely different problems:

| Approach | Changes | Best for | Not good for |
|---|---|---|---|
| **[Prompt engineering](../generation/prompt-engineering.md)** | Nothing — just the request | Quick iteration, tasks the base model can already mostly do | Deeply specialized behavior, new factual knowledge |
| **[RAG](../rag/rag.md)** | Nothing in the model — adds retrieved context at request time | Injecting knowledge that's current, private, or too large to fit in weights (see [RAG](../rag/rag.md)) | Changing *how* the model reasons, writes, or formats — it still answers in its default style |
| **Fine-tuning** | The model's weights, permanently | Changing behavior: consistent output format, tone, domain-specific reasoning patterns, following a rigid schema at scale | Injecting facts that change often — a fine-tuned fact is frozen at training time, same staleness problem as the base model |

The clearest way to separate them: **[RAG](../rag/rag.md) is for knowledge that changes; fine-tuning is for behavior that should stay fixed.** A support bot that needs today's ticket data should use [RAG](../rag/rag.md). A support bot that must always respond in a very specific tone, structure, and internal jargon regardless of the question is a better fine-tuning candidate. See [RAG](../rag/rag.md)'s "Why [RAG](../rag/rag.md) instead of just using an [LLM](../generation/llm.md)?" section for the retrieval side of this comparison.

In practice, the recommended sequence is to earn your way up the cost ladder: **try [prompt engineering](../generation/prompt-engineering.md) first (free, instant) → reach for [RAG](../rag/rag.md) when the model is missing knowledge it needs → fine-tune only once prompting and retrieval have both been tried and still don't produce consistent enough behavior.** Fine-tuning is more expensive to build, evaluate, and maintain (a new training run and evaluation pass every time requirements change) than either alternative, so it's deliberately the last resort, not the default.

Production systems in high-stakes domains (legal, medical, finance) increasingly combine both: fine-tuning for stable domain behavior and formatting, [RAG](../rag/rag.md) layered on top for the facts that change.

## How fine-tuning actually works

1. **Collect a dataset** of example [input/output](../../programming/fundamentals/io.md) pairs that demonstrate the desired behavior — hundreds to a few thousand high-quality examples is often enough for narrow behavioral changes (far less data than pretraining required).
2. **Choose a base model** to start from — fine-tuning adapts an existing pretrained model rather than training from scratch.
3. **Train** — continue the training process on the new dataset, adjusting weights so the model's outputs shift toward the demonstrated pattern, typically for a small number of passes over the data to avoid overfitting or degrading the model's general abilities.
4. **Evaluate** the fine-tuned model against the base model on held-out examples to confirm the behavior actually improved without regressing unrelated capabilities (see [LLM Evaluation](../evaluation/llm-evaluation.md)).
5. **Deploy** — the fine-tuned model is a distinct model/checkpoint you call instead of the base model.

## Full fine-tuning vs. LoRA/QLoRA

Updating every weight in a modern [LLM](../generation/llm.md) (full fine-tuning) is extremely expensive — it requires storing gradients and optimizer state for billions of parameters, and produces a full new copy of the model per task. Two parameter-efficient techniques have become the practical default:

| Technique | How it works | Why it matters |
|---|---|---|
| **[LoRA](lora.md)** ([Low-Rank Adaptation](lora.md)) | Freezes the base model's weights entirely and trains small, low-rank "adapter" matrices injected alongside them | Cuts training cost and storage sharply — the adapter is a small fraction of the base model's size, and multiple adapters can be swapped in for different tasks against the same frozen base |
| **QLoRA** | [LoRA](lora.md) combined with 4-bit quantization of the frozen base model | Enables fine-tuning large models on a single consumer-grade GPU, at a small cost in numerical precision |

As of 2026, [LoRA](lora.md) and QLoRA are the default approach for most teams doing fine-tuning — full fine-tuning is reserved for cases that specifically need it (e.g. foundation model providers training their own base models).

## When fine-tuning is the right call

Signals that fine-tuning is actually justified, rather than reached for prematurely:
- You need a **rigid, repeated behavior** at scale — a fixed output schema, a very specific tone, a narrow classification task — that prompting alone produces inconsistently.
- You've already tried [prompt engineering](../generation/prompt-engineering.md) and [RAG](../rag/rag.md) and neither closes the gap.
- You want to **distill** a smaller/cheaper model to mimic a larger, more expensive model's behavior on a narrow task, reducing latency and cost per request.
- The behavior needed is a **skill or pattern**, not a fact — facts belong in retrieval, patterns can be trained in.

Three concrete categories these signals usually show up as in practice:

| Category | Example | Why fine-tuning wins here |
|---|---|---|
| **Rigid output format** | Every answer must be valid [JSON](../../programming/fundamentals/json.md) with specific fields, or follow a formal memo template | Prompting can produce this *most* of the time; fine-tuning makes the format close to guaranteed, which matters once something downstream parses the output automatically |
| **Specialized, high-volume task** | Classifying thousands of support tickets into twenty fixed categories; extracting a fixed set of fields from invoices | A smaller fine-tuned model does one narrow task faster and cheaper per call than a large general-purpose model prompted to do the same thing — the distillation case above, made concrete |
| **Domain vocabulary** | A medical or legal domain where the base model keeps misreading field-specific terms or abbreviations | The base model's general training data under-represents this vocabulary; fine-tuning on in-domain examples corrects it directly, where more prompting or more retrieved context has diminishing returns |

## Fine-Tuning on Azure OpenAI

On [Azure OpenAI](../../cloud/azure/azure-openai.md), fine-tuning is a managed job rather than a self-run training script: upload a training file (JSONL of [input/output](../../programming/fundamentals/io.md) pairs) through [Azure AI Foundry](../../cloud/azure/azure-ai-foundry.md) or the API, start a fine-tuning job against a supported base model, and the result is a **custom model** — deployed like any other [Azure OpenAI](../../cloud/azure/azure-openai.md) deployment, with its own name and its own TPM/RPM quota, exactly as covered in [Azure OpenAI's quota model](../../cloud/azure/azure-openai.md#quota-is-two-dimensional-tpm-and-rpm). For a self-hosted open-source model instead, [LoRA](#full-fine-tuning-vs-loraqlora) is the practical default — training only small adapter layers keeps the GPU requirement far below what full fine-tuning would need.

## Related

- [Retrieval-Augmented Generation (RAG)](../rag/rag.md) — the alternative for injecting knowledge rather than changing behavior
- [Prompt Engineering](../generation/prompt-engineering.md) — the cheaper, first-resort technique to exhaust before fine-tuning
- [LLM Evaluation](../evaluation/llm-evaluation.md) — how to confirm a fine-tuned model actually improved on the target behavior
- [Large Language Models (LLMs)](../generation/llm.md) — the base model being adapted
- [Azure OpenAI](../../cloud/azure/azure-openai.md) — where a fine-tuned custom model is deployed, with its own TPM/RPM quota like any other deployment
- [Azure AI Foundry](../../cloud/azure/azure-ai-foundry.md) — the portal/project layer a fine-tuning job on [Azure OpenAI](../../cloud/azure/azure-openai.md) runs through
