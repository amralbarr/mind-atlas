# LoRA (Low-Rank Adaptation)

**LoRA** makes [fine-tuning](fine-tuning.md) cheap by never touching the base model's weights at all. Instead of updating a weight matrix directly, LoRA freezes it completely and learns a small *correction* alongside it — a correction expressed as the product of two much smaller matrices, which is where the "low-rank" in the name comes from.

## The Mechanism

For a frozen weight matrix `W` of size `d × d`, LoRA doesn't learn a new `d × d` update. It learns two small matrices `A` (`r × d`) and `B` (`d × r`), where the **rank** `r` is deliberately tiny compared to `d` (typically 4–64, versus a `d` in the thousands for a modern [LLM](../generation/llm.md)'s attention projections):

```
Standard fine-tuning:           LoRA:
  W_new = W + ΔW                  W_new = W + B·A
  ΔW is d × d (huge,               B is d × r, A is r × d
  fully trained)                   (both tiny, only these are trained)
                                    W itself never changes
```

**Why this is so much cheaper:** a `d × d` update has `d²` trainable parameters. `B·A` has only `2 × d × r`. With `d = 4096` and `r = 8` — realistic numbers for a mid-size LLM — that's roughly `65,000` trainable parameters instead of `16.7 million`, a reduction of over 250×. Training cost, GPU memory for gradients/optimizer state, and the resulting adapter's storage size all shrink by roughly the same factor.

## Where LoRA Gets Applied

LoRA is typically applied only to specific weight matrices, not the entire model — most commonly the attention mechanism's query and value projection matrices, which empirically capture most of what task-specific adaptation needs to change. Leaving most of the model's weights (including most of the feed-forward layers) completely untouched is part of why the technique works well with so few trainable parameters: it doesn't need to re-learn the model's general language ability, only nudge a narrow set of projections toward the new task.

## Key Hyperparameters

| Parameter | What it controls | Trade-off |
|---|---|---|
| **Rank (`r`)** | How expressive the low-rank update can be | Higher `r` can capture more complex adaptations but increases trainable parameters and risks overfitting on a small dataset; most tasks work well with `r` between 4 and 32 |
| **Alpha (`α`)** | A scaling factor applied to the adapter's output before adding it to the frozen weight | Controls how strongly the adapter's correction influences the final output relative to the frozen base — commonly set to roughly `2×` the rank as a starting heuristic |
| **Target modules** | Which weight matrices in the model get a LoRA adapter at all | Attention Q/V projections are the common default; adding more target modules (K projections, feed-forward layers) increases expressiveness and cost together |

## Serving: Merge, or Keep Separate for Multi-Tenant Adapters

Once trained, a LoRA adapter can be used in two different ways at inference time, and the choice matters operationally:

| Approach | How | Best for |
|---|---|---|
| **Merge into the base weights** | Compute `W' = W + B·A` once, offline, and deploy `W'` as a single ordinary model | A single fixed fine-tuned task — no extra inference-time overhead, but you get back a full-size model file, losing LoRA's storage advantage after merging |
| **Keep the adapter separate at serving time** | Load the frozen base model once, and apply different small adapters per request/tenant on top of it | Multi-tenant or multi-task serving — many task-specific adapters can share one frozen base model in memory, since each adapter is a tiny fraction of the base model's size |

The second case is what makes LoRA genuinely different from a cost-savings trick during training alone: a serving platform can hold one large frozen base model plus dozens of small adapters in memory, and pick the right adapter per request, rather than needing a full separate deployed model per fine-tuned task. [vLLM](vllm.md) and similar inference servers support exactly this — serving multiple LoRA adapters concurrently against one shared base model.

## QLoRA — LoRA Combined with Quantization

See [Fine-tuning — Full fine-tuning vs. LoRA/QLoRA](fine-tuning.md#full-fine-tuning-vs-loraqlora) for the comparison table: QLoRA adds 4-bit quantization of the frozen base model on top of LoRA's own parameter-efficiency, enabling [fine-tuning](fine-tuning.md) of large models on a single consumer-grade GPU at a small cost in numerical precision.

## Common Questions

**Does LoRA reduce inference latency, or only training cost?**
> It reduces training cost and adapter storage size directly. Inference latency is essentially unaffected either way — a merged adapter adds no extra computation at all, and an unmerged adapter applied at serving time adds only the cost of one small extra matrix multiplication, negligible compared to the base model's own forward pass.

**How is the right rank chosen for a given task?**
> Empirically, starting from a small value (e.g. `r=8`) and increasing only if the fine-tuned model's quality plateaus below what's needed — see [LLM Evaluation](../evaluation/llm-evaluation.md) for how to measure that quality gap against a held-out set. There's no universal correct rank; it depends on how different the target task's behavior is from the base model's existing behavior.

**Can multiple LoRA adapters be combined for one request?**
> Some serving setups support weighted combination of multiple adapters (e.g. blending a "formal tone" adapter with a "legal terminology" adapter), though this is less standardized than using one adapter per request and depends on the specific serving stack's support for it.

## Related

- [Fine-tuning](fine-tuning.md) — the broader technique LoRA makes parameter-efficient; includes the full fine-tuning vs. LoRA/QLoRA comparison
- [vLLM](vllm.md) — an inference server capable of serving multiple LoRA adapters concurrently against one shared frozen base model
- [LLM Evaluation](../evaluation/llm-evaluation.md) — how to measure whether a chosen rank/configuration actually closed the quality gap a fine-tuning effort was meant to close
- [GPU-Aware Scheduling](gpu-scheduling.md) — relevant once serving many adapters means scheduling which base model + adapter combination runs on which GPU
- [Large Language Models (LLMs)](../generation/llm.md) — the base model whose weights LoRA leaves untouched
