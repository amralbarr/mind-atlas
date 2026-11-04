# Claim Verification (Evidence Binding)

**Claim verification** — also called **evidence binding** — is the pipeline step that checks, for every individual claim in a generated answer, whether it's actually supported by a specific piece of retrieved evidence, *before* the answer reaches the user. It's the real-time, per-request **mechanism** that enforces groundedness; [Groundedness and Correctness](groundedness-and-correctness.md) is the **metric** that measures how well that mechanism — or the model's own behavior — is working, typically computed offline or in aggregate across many requests. A system can have a well-defined groundedness metric and still ship ungrounded answers to users if nothing actually *blocks* an unverified claim at request time — that enforcement gap is exactly what claim verification closes.

## Two Layers of Checking, Not One

| Layer | Checks | Catches |
|---|---|---|
| **1. Citation existence** | Does every cited source ID actually appear among the chunks that were retrieved for this request? | A hallucinated citation — the model invents a source number or filename that was never retrieved at all |
| **2. Claim-to-text support** | Does the cited chunk's *actual text* support the specific claim attributed to it? | A real citation attached to the wrong claim — the model cites a genuine chunk, but the sentence it's "supporting" isn't actually what that chunk says |

Layer 1 is cheap and deterministic — a set-membership check. Layer 2 is the harder, more valuable check: a citation can pass Layer 1 (the source genuinely was retrieved) while still failing Layer 2 (that source doesn't actually say what the model claims it says). Most systems implement Layer 1 first since it's nearly free; a mature system adds Layer 2 because Layer 1 alone still lets through a specific, dangerous failure mode — a technically-real citation attached to a fabricated claim.

### Layer 1 in Code

```python
def check_citation_exists(cited_ids: set[str], retrieved_ids: set[str]) -> bool:
    return cited_ids <= retrieved_ids   # every cited source must be among what was retrieved
```

See the [full worked version](../../../interview/interview-01/20-python-assistant-api-deep-dive.md#%E2%91%A2-evidence-validation) of this exact check in a real request pipeline — it's Layer ⑤ of that file's six-layer architecture, placed after generation and before the response is formatted.

### Layer 2 in Code

```python
def check_claim_supported(claim: str, cited_chunk_text: str, judge_model) -> bool:
    verdict = judge_model.classify(
        f"""Context: {cited_chunk_text}
        Claim: {claim}
        Is this claim directly stated or clearly implied by the context?
        Answer SUPPORTED, UNSUPPORTED, or CONTRADICTED."""
    )
    return verdict == "SUPPORTED"

def verify_answer(answer: str, cited_chunks: dict[str, str], judge_model) -> list[dict]:
    claims = split_into_claims(answer)          # one sentence/assertion per claim
    return [
        {
            "claim": claim.text,
            "cited_chunk": claim.cited_id,
            "supported": check_claim_supported(claim.text, cited_chunks[claim.cited_id], judge_model),
        }
        for claim in claims
    ]
```

This is the same [LLM](../generation/llm.md)-as-judge mechanic [Groundedness and Correctness](groundedness-and-correctness.md#measuring-groundedness) uses for scoring — the difference is *when* and *why* it runs: here it runs synchronously, per request, specifically to decide what to do with *this* answer before showing it, not to produce an aggregate score for a dashboard. `judge_model` here can be a full [LLM](../generation/llm.md) prompted for a classification, or a dedicated [NLI model](nli-model.md) — a small, fast, deterministic classifier purpose-built for exactly this premise→hypothesis entailment check, usually cheaper to run on every single claim than a full [LLM](../generation/llm.md) call.

## Handling Partial Support

A real answer is rarely 100% supported or 0% supported — the common case is a mix, and the decision of what to do with a partially-supported answer is a product decision, not just an engineering one:

| Strategy | Behavior | Trade-off |
|---|---|---|
| **Reject the whole answer** | Any unsupported claim fails the entire response; return abstention instead | Safest, but throws away genuinely useful supported content alongside the bad claim |
| **Strip the unsupported clause** | Remove or redact only the unsupported sentence, keep the rest | Preserves useful content, but risks leaving an answer that reads oddly or loses necessary context |
| **Flag inline, show both** | Return the full answer, but visibly mark which claims are supported vs. not (e.g. a warning icon per sentence) | Most transparent, but pushes the verification decision onto the end user instead of the system |
| **Regenerate with a tighter prompt** | Re-run generation once, explicitly excluding what failed verification | Costs an extra model call and adds latency, but can recover a usable answer instead of abstaining outright |

High-assurance systems (financial, legal, medical, HR data) generally default to reject-or-regenerate; lower-stakes assistants more often ship the flag-inline strategy, trading a small UX cost for not discarding generally-useful answers over one soft claim.

## Presenting Evidence So a Human Can Actually Verify It

Binding a claim to a citation *number* is necessary but not sufficient for a user to verify it themselves — the practical bar is higher:

- **Show the exact source span**, not just a document name or ID — the specific paragraph or sentence the claim is drawn from, ideally highlighted in place.
- **Make the source openly inspectable**, respecting the same [authorization](../../security/authorization/authorization.md) that gated retrieval in the first place — a citation link must re-check permission at click time, not just at retrieval time, in case access changed between the two.
- **Distinguish "cited" from "verified"** in the UI if Layer 2 checking is in place — a citation that passed Layer 1 only (exists) is a weaker guarantee than one that passed Layer 2 (semantically supported), and a sufficiently careful UI can signal that difference rather than treating every citation as equally trustworthy.

## Why This Matters More Than It Looks

The dangerous failure mode isn't an answer that's obviously wrong — it's [Groundedness and Correctness](groundedness-and-correctness.md#the-core-distinction)'s "Answer C" pattern: a response where the first clause is genuinely grounded and correct, building trust, and a later clause quietly adds an unsupported claim riding on that same trust. Claim verification exists specifically to catch that pattern at the individual-claim level — an answer-level groundedness score can still average out to "looks fine" even when one specific sentence in it is fabricated, because the score is an aggregate over claims, not a gate on each one.

## Common Questions

**Isn't this the same thing as [RAGAS](ragas.md)'s faithfulness score?**
> No — [RAGAS](ragas.md)'s faithfulness score is computed to *evaluate* a pipeline, usually offline over a test set, to answer "how grounded is this system in general?" Claim verification runs online, per live request, to answer a narrower, more consequential question: "should *this specific answer* be shown to *this specific user* right now?" The same underlying claim-vs-context classification logic can power both, but the metric and the mechanism serve different purposes and typically run at different points in the system.

**Does Layer 1 (citation existence) ever catch something Layer 2 would miss?**
> Yes — Layer 1 catches an invented source ID outright (the claim cites `doc_47` and `doc_47` was never retrieved at all), which Layer 2 wouldn't even get to check since there's no real chunk text to compare against. They're complementary, not redundant: Layer 1 catches fabricated sources, Layer 2 catches real sources being misquoted.

**What should the system do if claim verification itself fails or times out?**
> Fail closed — treat an unverifiable claim the same as an unsupported one (abstain or strip it), never the same as a verified one. A verification step that fails open defeats its own purpose the moment it's under load or hits a transient error.

## Related

- [Groundedness and Correctness](groundedness-and-correctness.md) — the metric this mechanism enforces at request time; read this first for the SUPPORTED/UNSUPPORTED/CONTRADICTED classification this file's Layer 2 reuses
- [NLI Model](nli-model.md) — the lightweight, dedicated classifier alternative to an [LLM](../generation/llm.md)-as-judge for the Layer 2 check
- [RAGAS](ragas.md) — the evaluation library implementing the same claim-vs-context judgment as a scoring tool rather than a live gate
- [RAG](../rag/rag.md) — the architecture that makes evidence available to bind claims to in the first place
- [Structured Output](../generation/structured-output.md) — constraining the model to emit claims with explicit citation IDs attached, a prerequisite for Layer 1 checking to even be possible
- [Deep Dive — Python Assistant API](../../../interview/interview-01/20-python-assistant-api-deep-dive.md#%E2%91%A2-evidence-validation) — Layer 1's exact implementation inside a full six-layer request pipeline
- [Authorization](../../security/authorization/authorization.md) — must be re-checked when a user clicks through to a cited source, not assumed from retrieval-time access
- [Prompt Injection](../../security/attacks/prompt-injection.md) — a different threat to the same evidence: injected content masquerading as a legitimate source a claim could get bound to
- [RAG & Grounding — What does evidence binding mean beyond adding citations?](../../../interview/interview-01/01-rag.md) — the interview-prep answer this concept formalizes
- [Evaluation Workshop E06](../../../interview/interview-01/15-evaluation-metrics-workshop.md) — the same per-claim rubric as a worked exercise
