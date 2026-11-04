# Azure AI Foundry

Azure AI Foundry (formerly **[Azure](azure.md) AI Studio**, renamed 2024) is Microsoft's unified platform for building, deploying, evaluating, and managing AI applications on [Azure](azure.md). It bundles [Azure](azure.md) OpenAI, [Azure AI Search](azure-ai-search.md), model catalog, prompt flow tooling, and evaluation frameworks under one portal and SDK. See [Azure OpenAI — the Service vs. the Platform](azure-openai.md#azure-openai-the-service-vs-azure-ai-foundry-the-platform) for the specific service-vs-platform distinction with [Azure OpenAI](azure-openai.md), the component most often confused with Foundry itself.

## Key Services

| Service                    | What it does                                                                          | Self-hosted equivalent                                   |
| -------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **[Azure](azure.md) OpenAI Service**   | Managed GPT-4o, GPT-4, text-embedding-3, DALL-E endpoints                             | [vLLM](../../ai/infrastructure/vllm.md) inference server |
| **[Azure AI Search](azure-ai-search.md)**        | [Hybrid search](../../ai/retrieval/hybrid-search.md) (vector + [BM25](../../ai/retrieval/bm25.md)/keyword), semantic re-ranking, enterprise-scale indexing | pgvector + custom [hybrid search](../../ai/retrieval/hybrid-search.md)                          |
| **[Azure Machine Learning](azure-ml.md)** | MLOps — experiment tracking, model registry, training pipelines                       | MLflow + custom infra                                    |
| **Prompt Flow**            | Visual / code-based tool for building and evaluating [LLM](../../ai/generation/llm.md) pipelines                    | Custom [FastAPI](../../programming/python/fastapi.md)/[LangChain](../../ai/agents/langchain.md) pipelines                       |
| **[Azure](azure.md) Content Safety**   | Content moderation API for [LLM](../../ai/generation/llm.md) inputs/outputs                                         | Custom filters                                           |
| **Model Catalog**          | Deploy open-source models (Llama, Mistral, Phi) as managed endpoints                  | [vLLM](../../ai/infrastructure/vllm.md) with HuggingFace models                             |

## Azure AI Search — The RAG Retrieval Layer

[Azure AI Search](azure-ai-search.md) is the managed hybrid ([BM25](../../ai/retrieval/bm25.md) + vector) search and semantic-ranking service that Foundry bundles as its [RAG](../../ai/rag/rag.md) retrieval layer. See its own concept file: [Azure AI Search](azure-ai-search.md).

## Mapping Self-Hosted Stack to Azure

| Self-hosted                                              | [Azure](azure.md) equivalent                                        |
| -------------------------------------------------------- | ------------------------------------------------------- |
| [vLLM](../../ai/infrastructure/vllm.md) inference server | [Azure OpenAI Service](azure-openai.md) endpoint                           |
| pgvector ([PostgreSQL](../../databases/relational/postgresql.md))                                    | [Azure AI Search](azure-ai-search.md)                                         |
| [OpenTelemetry](../../backend/observability/opentelemetry.md) + [Grafana](../../backend/observability/grafana.md)                                  | [Azure](azure.md) Monitor + Application Insights                    |
| Custom [CI/CD](../../devops/ci-cd.md)                                             | Azure DevOps / [GitHub Actions](../../devops/github-actions.md)                           |
| [Azure AD](microsoft-entra-id.md) / [JWT](../../security/auth/jwt.md) | [Microsoft Entra ID](microsoft-entra-id.md) (see below) |

## What Azure AI Foundry Does NOT Do Automatically

- **Document-level permission enforcement** — Entra ID handles identity (who you are), but the application must still enforce which documents a user is allowed to retrieve. A missing filter = cross-department data leak.
- **Hallucination prevention** — content safety filters catch harmful content; groundedness must be enforced by the application (citation verification, abstention instructions in the [system prompt](../../ai/generation/system-prompt.md)).
- **Prompt versioning** — prompt changes must be managed as code; Foundry's Prompt Flow helps but doesn't enforce it.

## Related

- [Microsoft Entra ID](microsoft-entra-id.md) — the Azure AD identity provider Foundry auth maps to, including the [JWT](../../security/auth/jwt.md) access tokens it issues
- [JWT](../../security/auth/jwt.md) — the token format Entra ID issues and a self-hosted gateway would validate instead
- [Databricks](../data/databricks.md) — upstream data engineering and ML platform that feeds curated data into [Azure AI Search](azure-ai-search.md)
- [ADLS](adls.md) — the raw storage layer that [Databricks](../data/databricks.md) reads from on Azure
- [Azure](azure.md)
- [Azure AI services](azure-ai-services.md) — the family of pre-built AI APIs (Language, Vision, Speech, Document Intelligence, Content Safety, etc.) that Foundry bundles alongside [Azure OpenAI](azure-openai.md)
- [Azure AI Search](azure-ai-search.md) — the [hybrid search](../../ai/retrieval/hybrid-search.md) + semantic ranking service that is Foundry's [RAG](../../ai/rag/rag.md) retrieval layer
- [vLLM](../../ai/infrastructure/vllm.md) — the self-hosted inference-server equivalent to [Azure OpenAI Service](azure-openai.md)
- [RAG](../../ai/rag/rag.md)
- [Embeddings](../../ai/ingestion/embeddings.md)
- [Hybrid Search](../../ai/retrieval/hybrid-search.md)
- [Vector Database](../../ai/retrieval/vector-database.md)
