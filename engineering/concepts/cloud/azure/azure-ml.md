# Azure Machine Learning (Azure ML)

Azure Machine Learning is Microsoft's MLOps platform — experiment tracking, model registry, training-job orchestration, and managed model deployment — for classical ML and deep learning workloads that read training data from [ADLS](adls.md) or other [Azure](azure.md) storage. It predates [Azure AI Foundry](azure-ai-foundry.md) and still exists as its own service; Foundry's own "Azure Machine Learning" row in its services table (see [Azure AI Foundry — Key Services](azure-ai-foundry.md)) points back to this same product rather than Foundry replacing it — Foundry is focused specifically on [LLM](../../ai/generation/llm.md)/generative-AI application building, while Azure ML covers the broader classical-ML lifecycle.

## Core concepts

| Term | Meaning |
|---|---|
| **Workspace** | The top-level container for an Azure ML project — datasets, experiments, models, and compute all live inside one workspace |
| **Experiment / Run** | A tracked execution of a training script, logging metrics, parameters, and output artifacts for comparison across runs |
| **Compute target** | The actual hardware a job runs on — a managed compute cluster (autoscaling CPU/GPU nodes), compute instance (a single dev VM), or [Kubernetes](../../distributed-systems/kubernetes/ingress.md) |
| **Model registry** | Versioned storage for trained models, with metadata and lineage back to the run that produced them |
| **Managed endpoint** | A deployed model exposed as a scalable, authenticated [HTTP](../../networking/http.md) API — Azure ML's answer to "serve this model in production" |
| **Pipeline** | A reusable, multi-step ML workflow (data prep → train → evaluate → register) defined as code |

## Self-hosted equivalent

The self-hosted analog most often cited alongside Azure ML in this handbook's [Azure](azure.md)-vs-self-hosted comparisons is **MLflow** (experiment tracking, model registry) **plus custom infrastructure** for the compute-orchestration and serving pieces Azure ML provides as one managed product.

## Related

- [ADLS](adls.md) — a common training-data source for Azure ML jobs
- [Azure AI Foundry](azure-ai-foundry.md) — the newer, [LLM](../../ai/generation/llm.md)/generative-AI-focused platform that references Azure ML as the classical-ML counterpart in its own services table
- [Fine-tuning](../../ai/infrastructure/fine-tuning.md)
- [Model Lifecycle Management](../../ai/infrastructure/model-lifecycle-management.md)
