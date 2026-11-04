# Langfuse

Langfuse is an open-source [LLM](../generation/llm.md) engineering platform for tracing, evaluating, and managing prompts in production [LLM](../generation/llm.md)/agent applications. Its core is MIT-licensed, so it can be self-hosted with full data ownership, or run as a managed Langfuse Cloud instance — unlike [LangSmith](langsmith.md), which gates self-hosting behind its Enterprise tier. See [Langfuse vs. LangSmith](../../../overviews/ai/langfuse-vs-langsmith.md) for the full comparison.

## What it actually does

| Capability | What it covers |
|---|---|
| **Tracing** | Captures every [LLM](../generation/llm.md) and non-[LLM](../generation/llm.md) call in a request — retrieval, embedding, tool calls, API calls — as a nested trace, with multi-turn conversations grouped into sessions and multi-agent flows visualized as graphs |
| **Prompt management** | Versions prompts outside application code, supports a collaborative playground for iterating on them, and links deployed prompt versions back to the production traces they generated |
| **Evaluation** | Runs [LLM-as-judge](llm-evaluation.md) scoring, custom code-based evaluators, and user feedback/manual labeling against [datasets](fixed-evaluation-dataset.md) — the same offline-regression-testing pattern described generically in [LLM Evaluation](llm-evaluation.md), wired directly to the traces that produced each output |
| **Dashboards** | Cost, latency, and quality metrics broken down by prompt version, model, or user, with alerting via Slack/[GitHub Actions](../../devops/github-actions.md)/[webhooks](../../backend/api/webhooks.md) |

## Basic usage

```bash
pip install langfuse
```

```python
from langfuse import get_client, observe
from langfuse.openai import openai  # drop-in replacement for the openai package

langfuse = get_client()

@observe()
def answer_question(question: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content

answer_question("What was Q3 revenue?")
```

The `@observe()` decorator wraps a function as a trace span, capturing its inputs, outputs, timing, and any nested calls automatically. Swapping the `openai` import for `langfuse.openai`'s wrapper is enough to get every underlying [LLM](../generation/llm.md) call logged without touching the call sites themselves — the same low-friction integration pattern Langfuse also offers for [LangChain](../agents/langchain.md) and [LlamaIndex](../agents/llamaindex.md). Scores can also be attached to a trace after the fact, e.g. from an automated evaluator or a human reviewer:

```python
langfuse.create_score(trace_id="...", name="correctness", value=0.8)
```

## Self-hosted vs. Cloud

Because the core platform is open-source, teams with strict data-residency requirements commonly self-host it ([Docker Compose](../../containers/docker-compose.md) for small deployments, [Kubernetes](../../distributed-systems/kubernetes/ingress.md) for production scale) and pay nothing beyond their own infrastructure; Langfuse Cloud trades that operational burden for a managed, usage-priced SaaS tier. This open-core-first positioning is the main practical reason teams pick Langfuse over [LangSmith](langsmith.md) when self-hosting matters.

## Where it fits in an LLM/agent workflow

Langfuse sits alongside, not inside, the application: it's typically wired in early (via the OpenAI/[LangChain](../agents/langchain.md)/[LlamaIndex](../agents/llamaindex.md) integrations) so that every production call is traced from day one, then used continuously the way [LLM Evaluation](llm-evaluation.md) and [RAGAS](ragas.md) describe — scoring a [fixed evaluation dataset](fixed-evaluation-dataset.md) on every prompt or model change, with traces providing the debugging context (exact inputs, retrieved chunks, intermediate tool calls) that a bare evaluation score alone doesn't give you.

## Related

- [Langfuse vs. LangSmith](../../../overviews/ai/langfuse-vs-langsmith.md) — full comparison with the [LangChain](../agents/langchain.md)-affiliated alternative
- [LangSmith](langsmith.md) — the closest competing platform
- [LLM Evaluation](llm-evaluation.md) — the evaluation methodology Langfuse's scoring features implement against live traces
- [RAGAS](ragas.md) — a metrics library Langfuse can run as one of its evaluators
- [Fixed Evaluation Dataset](fixed-evaluation-dataset.md) — what Langfuse's dataset/experiment feature runs regression tests against
- [LangChain](../agents/langchain.md) / [LlamaIndex](../agents/llamaindex.md) — frameworks Langfuse integrates with directly for automatic tracing
