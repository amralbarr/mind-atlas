# Decoupling Pipeline Stages

> Each stage in a pipeline should be independently deployable and communicate via APIs or queues.

## What "Decoupling Stages" Actually Means

Each step in a pipeline should be a separate service or module that does **not** depend on the internal code of other steps. Instead, it depends only on:

- Its input data (from an API or message queue).
- Its output contract (a [JSON](../../programming/fundamentals/json.md) payload or schema).

## Bad Design: Tightly Coupled

Everything lives inside one monolith:

```text
ocr() → chunk() → embed() → rag() → generate()
```

Problems with this approach:

- Changing chunking logic means redeploying everything.
- It's hard to scale just one stage.
- One failure can break the entire pipeline.
- Stages can't be debugged independently.

## Good Design: Decoupled Stages

Each stage becomes independent:

```text
OCR Service → Queue → Chunking Service → Queue → Embedding Service → Queue → LLM Service
```

### 1. Independently Deployable Services

Example split:

- [OCR](../../ai/ingestion/ocr.md) service (Python/[FastAPI](../../programming/python/fastapi.md))
- Chunking service (Node or Python)
- Embedding service (worker)
- [LLM](../../ai/generation/llm.md) service (API wrapper)

Each has its own codebase, deployment, and scaling rules.

### 2. Communication via APIs or Queues

There are two main approaches.

#### Option A — API-Based Communication (Synchronous)

```text
OCR Service → calls Chunking API → calls Embedding API
```

**Pros:** simple, easy to debug.
**Cons:** tightly timed, slow if one service lags, failures cascade.

#### Option B — Queue-Based Communication (Recommended)

```text
OCR → Queue → Chunk Worker → Queue → Embedding Worker
```

Typically implemented with [queues](../messaging/queues.md) or a [message broker](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) such as [RabbitMQ](../messaging/rabbitmq.md), [Kafka](../messaging/kafka.md), Redis-based queues, or [SQS](../messaging/sqs.md).

**Pros:** highly scalable, fault tolerant, asynchronous, retries built in. This is the pattern most production data/AI pipelines use.

## Example: Document-to-Slides Pipeline

A pipeline such as:

```text
OCR → cleaning → chunking → embeddings → clustering → RAG → validation → slides
```

maps naturally onto independent services or workers:

| Stage | Type |
|---|---|
| [OCR](../../ai/ingestion/ocr.md) | API service |
| Chunking | Worker |
| [Embeddings](../../ai/ingestion/embeddings.md) | GPU worker |
| [RAG](../../ai/rag/rag.md) | Retrieval service |
| Validation | Stateless service |
| Slides | Rendering service |

## Why Decoupling Matters

**Independent scaling** — if [embeddings](../../ai/ingestion/embeddings.md) are slow, scale only the embedding workers, not the whole system.

**Fault isolation** — if the [LLM](../../ai/generation/llm.md) service fails, [OCR](../../ai/ingestion/ocr.md) and chunking can keep running.

**Replaceability** — components can be swapped (e.g. a hosted [LLM](../../ai/generation/llm.md) for a local one, [FAISS](../../ai/retrieval/vector-stores/faiss.md) for pgvector, Tesseract for PaddleOCR) without touching other stages.

**Parallel execution** — independent units of work can run concurrently:

```text
Chunk A → embedding
Chunk B → embedding
Chunk C → embedding
```

## Mental Model

Think of it like an assembly line:

```text
Factory:
[OCR] → [Cleaner] → [Splitter] → [AI Engine] → [Validator]
```

Each machine does one job, doesn't care who consumes its output, and only follows the [input/output](../../programming/fundamentals/io.md) contract.

## Summary Answer

> Decoupling stages means designing each pipeline step as an independent service that communicates through well-defined APIs or [message queues](../messaging/queues.md) instead of direct function calls. This allows each stage to be deployed, scaled, and maintained independently. In production pipelines, queue-based communication is usually preferable because it enables async processing, fault tolerance, and better scalability.

## Key Takeaway

```text
Decoupling = no shared runtime, only shared contracts (data + events)
```

## Related

- [Saga Pattern](saga-pattern.md)
- [Fan-Out Architecture](fan-out-architecture.md)
- [Queues](../messaging/queues.md)
- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
