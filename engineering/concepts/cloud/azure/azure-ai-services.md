# Azure AI Services

[Azure](azure.md) AI services (formerly **[Azure](azure.md) Cognitive Services**, rebranded 2023) is Microsoft's umbrella brand for its portfolio of pre-built and customizable AI APIs — vision, speech, language, document processing, content moderation, and more — that let developers add AI capabilities to applications without training models from scratch. Microsoft's current docs refer to these individually as "Foundry Tools," reflecting that they're now surfaced through [Azure AI Foundry](azure-ai-foundry.md) as well as standalone.

## What It Is

Azure AI services are a family of independently billable, independently callable [REST](../../backend/api/rest.md) APIs/SDKs — not one single product. Each service solves a specific pre-built AI task:

```
Your application
    ↓ REST API / SDK call
Azure AI services resource (single-service or multi-service)
    ↓
Managed model (vision, language, speech, etc.) — no training required
    ↓
Structured result back to your application
```

This is the key distinction from **[Azure](azure.md) OpenAI** / the **model catalog**: Azure AI services are task-specific, pre-built APIs (e.g. "extract key phrases from this text," "transcribe this audio," "pull fields out of this invoice PDF") rather than general-purpose generative models you prompt.

## Key Services

| Service                            | What it does                                                                                                                       |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **[Azure](azure.md) AI Language**              | [NLP](../../ai/nlp.md): sentiment analysis, key phrase extraction, named entity recognition, PII detection, summarization, custom text classification |
| **[Azure](azure.md) AI Speech**                | Speech-to-text, text-to-speech, speech translation, speaker recognition                                                            |
| **[Azure](azure.md) AI Vision**                | Image/video analysis: object detection, [OCR](../../ai/ingestion/ocr.md), image captioning, tagging                                                             |
| **[Azure](azure.md) AI Document Intelligence** | Extracts structured data (fields, tables, key-value pairs) from documents — invoices, receipts, forms, ID cards                    |
| **[Azure AI Content Safety](../../security/attacks/azure-prompt-shields.md)**        | Detects harmful/unwanted content (hate, violence, self-harm, sexual) in text and images — used to moderate [LLM](../../ai/generation/llm.md) inputs/outputs      |
| **[Azure](azure.md) AI Translator**            | Text translation across 100+ languages                                                                                             |
| **[Azure AI Search](azure-ai-search.md)**                | Search-as-a-service with hybrid (keyword + vector) search and semantic ranking — see its own [concept file](azure-ai-search.md)    |
| **Azure AI Custom Vision**         | Train custom image classification/object detection models on your own labeled images                                               |
| **Azure AI Content Understanding** | Analyzes and extracts structured insight from multimodal content (documents, audio, video)                                         |
| **Azure AI Immersive Reader**      | Reading-comprehension aids (text-to-speech, translation, grammar breakdown) embeddable in apps                                     |

A few older services (Anomaly Detector, Content Moderator, LUIS, Metrics Advisor, Personalizer, QnA Maker) are retired/retiring and still listed for existing deployments only — not for new builds.

## Azure AI Services vs Azure AI Foundry

These two names are frequently confused; the distinction matters for interviews:

| | Azure AI services | [Azure AI Foundry](azure-ai-foundry.md) |
|---|---|---|
| **What it is** | The family of pre-built AI APIs themselves (Language, Vision, Speech, Document Intelligence, Content Safety, etc.) | The unified dev/ops platform and portal for building, deploying, and evaluating AI applications |
| **Scope** | Individual, task-specific capabilities | Orchestration layer: bundles [Azure OpenAI](azure-openai.md), the model catalog, [Azure AI Search](azure-ai-search.md), prompt flow, evaluation tooling, and Azure AI services together |
| **Consumption** | Call its [REST](../../backend/api/rest.md) API/SDK directly, standalone, with no Foundry project needed | A project/workspace that wires multiple services (including Azure AI services) together into one application |
| **Analogy** | The individual tools in the toolbox | The workbench that organizes and connects the tools |

In short: **Azure AI services can be consumed standalone, or as building blocks inside [Azure AI Foundry](azure-ai-foundry.md)** — Foundry does not replace them, it's a layer on top that makes composing them (plus [Azure OpenAI](azure-openai.md) and custom models) into one application easier to build, test, and deploy.

## Authentication & Resource Model

Azure AI services resources come in two flavors:

- **Single-service resource** — provisions one service (e.g. just Language) with its own endpoint and key. Simpler billing/quota isolation per service.
- **Multi-service resource ("Azure AI services" resource)** — one endpoint and key that can call most of the AI services under one umbrella, simplifying credential management when an app uses several services together.

[Authentication](../../security/auth/authentication.md) is via a resource key (subscription key) or [Microsoft Entra ID](microsoft-entra-id.md) token; network access can be restricted with Azure Virtual Networks / private endpoints.

## Pricing Model

Billing is usage-based per service: each pricing tier defines a maximum transactions-per-second rate, which features are enabled at that tier, and a cost for a set volume of transactions (overage billed beyond that). Most services offer a free tier (SKU `F0`) for evaluation/small-scale use, separate from a paid standard tier (`S0` and up).

## Consumption Options

- **[REST](../../backend/api/rest.md) API / client SDKs** (Python, C#, Java, JavaScript, etc.) — the primary way applications call these services directly
- **[Azure AI Foundry](azure-ai-foundry.md) portal** — try and wire services together visually, without writing boilerplate client code first
- **On-premises containers** — several of the services can run in [Docker](../../containers/docker.md) containers for data residency/latency/compliance reasons, rather than calling the cloud endpoint directly
- **[CI/CD](../../devops/ci-cd.md)** — Azure DevOps / [GitHub Actions](../../devops/github-actions.md) pipelines for training and deploying custom models (e.g. Custom Speech, Custom Vision)

## Related

- [Azure AI Foundry](azure-ai-foundry.md) — the unified platform that bundles Azure AI services, Azure OpenAI, and the model catalog into one dev/ops experience
- [Azure AI Search](azure-ai-search.md) — one of the Azure AI services, with [hybrid search](../../ai/retrieval/hybrid-search.md) and semantic ranking as its specialty
- [NLP](../../ai/nlp.md) — the field Azure AI Language implements, including the classical-vs-[LLM](../../ai/generation/llm.md)-based task taxonomy
- [Microsoft Entra ID](microsoft-entra-id.md) — identity provider used for Entra-token [authentication](../../security/auth/authentication.md) to Azure AI services resources
- [Azure](azure.md)
