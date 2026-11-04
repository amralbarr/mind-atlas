# Message Queues

A **message broker** (or message queue) is a system that acts as an intermediary between services so they can communicate without talking to each other directly, decoupling producers from consumers.

> A message broker is a software system that receives, stores, and forwards messages between applications or services.

## The Basic Idea

Instead of tight coupling:

```text
Service A → directly calls → Service B
```

Services communicate through a broker:

```text
Service A → Message Broker → Service B
```

## What a Broker Actually Does

A message broker typically performs three jobs:

1. **Receives messages** — Service A sends a message, e.g. `{ "job": "process_image", "id": 123 }`.
2. **Stores messages safely** — it puts them in a queue or topic so nothing is lost.
3. **Delivers messages** — Service B (a worker) picks them up when it's ready.

**Analogy:** think of it like a post office. Service A is the sender, the broker is the post office, and Service B is the receiver. The sender doesn't need to know where the receiver is, whether it's online, or how fast it processes — the post office handles delivery.

## Why Message Brokers Exist

They solve four recurring problems in distributed systems:

### Decoupling

Services don't depend on each other directly — a producer only needs to know about the broker, not the consumer.

### Async processing

Service A doesn't wait for Service B. For example, an [OCR](../../ai/ingestion/ocr.md) step can finish, hand off a job, and move on immediately.

### Reliability

If Service B is down, messages stay in the broker and are processed once it recovers.

### Scalability

Adding capacity is as simple as adding more workers behind the same queue: `1 queue → 10 workers`.

## Where Brokers Fit in a Pipeline

In an AI processing pipeline, every stage typically talks to the next through the broker rather than calling it directly:

```text
OCR → message broker → chunking worker
chunking → message broker → embedding worker
embedding → message broker → RAG service
```

A fuller architecture looks like this:

```text
Client / API (upload / request)
        │
        v
API Gateway / Orchestrator
        │
        v
   MESSAGE BROKER (RabbitMQ / Kafka / SQS / Redis)
   │          │            │
   v          v            v
OCR Worker  Chunking    Embedding Worker
   │          │             │
   └──────────┴──────┬──────┘
                      v
              Vector Database (pgvector / FAISS)
                      │
                      v
                 RAG Service
                      │
                      v
                 LLM Service
                      │
                      v
          Post-Processing (validation / cleanup)
                      │
                      v
        Output Generator (slides / report / API)
```

Each arrow in that diagram is really `stage → BROKER → next stage`, not a direct call. Every stage stays independent, so:

- **It's fully decoupled** — each service can be developed, deployed, and fail independently.
- **It scales unevenly** — you can run 10 [OCR](../../ai/ingestion/ocr.md) workers and 50 embedding workers if that's where the bottleneck is, without touching the rest of the pipeline.
- **It's fault tolerant** — if the [LLM](../../ai/generation/llm.md) service crashes, upstream stages keep processing and their output simply queues up.
- **It's async** — no service blocks waiting on another.
- **It's easy to extend** — a new stage (translation, sentiment analysis, a review step) can subscribe to the broker without changing any existing stage.

**Senior-level summary:** A message broker decouples pipeline stages into independent, horizontally scalable workers. Each stage communicates via events instead of direct calls, enabling asynchronous processing, fault isolation, and dynamic scaling.

## Polling-Based Orchestration vs. a Real Queue

A common evolutionary stage for pipeline systems is a **database-backed orchestrator**: a table of pipeline runs, a `checkQueue()` job that polls it on an interval, and a sequential loop that executes each step in order. This pattern is extremely common in early-stage systems and isn't a bad starting point — it's simple, debuggable, and deterministic, and it typically comes with useful properties like persistent state and the ability to resume a run from a failed step.

It does, however, have real limitations once a system needs to scale:

- **Polling inefficiency** — repeatedly asking "is there something new?" wastes cycles and delays execution instead of reacting immediately.
- **Single orchestrator bottleneck** — one process coordinates everything, so it becomes both a scaling limit and a single point of failure.
- **Tight coupling to the database** — the database ends up acting as queue, state machine, scheduler, and event system all at once, risking overload.
- **No real async execution model** — even "sequential" steps are still driven by one runtime loop rather than independent workers.
- **Hard to scale individual steps** — a heavy [OCR](../../ai/ingestion/ocr.md) stage and a slow [LLM](../../ai/generation/llm.md) stage can't be scaled independently when they share one orchestrator loop.

The typical upgrade path is incremental rather than a full rewrite:

1. **Replace polling with an event trigger** — an insert into the run table triggers execution immediately (a DB trigger, listener, or in-process event emitter) instead of a periodic poll.
2. **Introduce a lightweight queue** — Redis is a common first step; [RabbitMQ](rabbitmq.md) is a common next one.
3. **Split the orchestrator into workers** — instead of one function running every stage, dedicated [OCR](../../ai/ingestion/ocr.md) / chunking / [RAG](../../ai/rag/rag.md) / [LLM](../../ai/generation/llm.md) workers each listen for their own queue events.
4. **Make each step stateless** — a step reads its input from the DB or queue, does its work, and writes its output back, rather than living inside one long-running loop.

The end state looks like:

```text
API → Queue → Workers → DB (state) → next queue event
```

In short: a database-driven orchestrator is a reasonable starting architecture, but a queue-based, event-driven pipeline is what to move toward once scaling, parallel runs, throughput, or fault isolation start to matter.

## Choosing a Broker

Redis is the simplest starting point, [RabbitMQ](rabbitmq.md) and [Kafka](kafka.md) are the common production upgrades, and [SQS](sqs.md) is the default for [AWS](../../cloud/infrastructure/aws.md)-native deployments. See [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) for a full comparison of when to use each.

## Related

- [Mesh Architecture](../patterns/mesh-architecture.md)
- [Decouple Stages](../patterns/decouple-stages.md)
- [Pipeline Orchestration](../../ai/infrastructure/pipeline-orchestration.md)
- [RAG](../../ai/rag/rag.md)
- [System Design](../../backend/architecture/system-design.md)
- [Model Lifecycle Management](../../ai/infrastructure/model-lifecycle-management.md) — batch mode drains a queue while a heavy model stays warm

## See Also

- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [Redis Lists](redis-lists.md)
- [FIFO vs LIFO](../patterns/fifo-lifo.md)
- [Backpressure](../patterns/backpressure.md)
- [Dead-Letter Queue](dead-letter-queue.md)
