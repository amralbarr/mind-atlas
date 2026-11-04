# Fan-Out Architecture

**Fan-out** is a design pattern where one event or request is distributed to multiple independent consumers in parallel.

## Core Idea

Instead of:

```text
One → One
```

you get:

```text
One → Many (parallel)
```

A single producer sends a message, and multiple services receive and process it independently.

## Example

Imagine a system emits a `UserSignedUp` event. With fan-out, several services can react at once:

- Email Service → sends a welcome email
- Analytics Service → tracks the signup
- Notification Service → sends a push notification
- Personalization Service → tailors onboarding content

All of these run **at the same time**, not sequentially.

## How It's Implemented

Fan-out is typically implemented with message brokers or event-streaming systems — see [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md).

In [RabbitMQ](../messaging/rabbitmq.md), this is literally called a **fanout exchange**: one message is broadcast to every bound queue.

## Architecture Flow

```text
        [Producer]
             |
     ┌───────┼────────┐
     ↓       ↓        ↓
[Service A] [Service B] [Service C]
```

Each service has its own queue, processes independently, and can scale separately.

## Why Use Fan-Out?

### Advantages

- Parallel processing → faster systems.
- Decoupling → services don't depend on each other.
- Scalability → consumers can be added or removed easily.
- Flexibility → new features can subscribe without touching the producer.

### Challenges

- Harder debugging — many async flows to trace.
- Event duplication needs to be handled.
- Ordering across consumers is not guaranteed.
- Requires idempotent consumers.

## Fan-Out vs. Sequential

| Type | Flow | Speed | Coupling |
|---|---|---|---|
| Sequential | A → B → C | Slow | Tight |
| Fan-out | A → (B, C, D) | Fast | Loose |

## Example: Document Processing Pipeline

A sequential pipeline like:

```text
OCR → Clean → Chunk → Embeddings → Slides
```

can fan out immediately after [OCR](../../ai/ingestion/ocr.md), so independent steps run in parallel instead of one after another:

```text
OCR
  ├── Clean Text
  ├── Extract Metadata
  ├── Detect Language
  └── Store Raw Data
```

## Relation to Other Patterns

Fan-out works well alongside:

- Event-driven architecture
- The [saga pattern](saga-pattern.md) — an individual saga step can itself fan out
- [Pub/Sub](../messaging/publish-subscribe.md) systems

## One-Line Definition

> Fan-out architecture broadcasts one event to multiple independent consumers for parallel processing.

## Related

- [Decoupling Pipeline Stages](decouple-stages.md)
- [Saga Pattern](saga-pattern.md)
- [Queues](../messaging/queues.md)
- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
