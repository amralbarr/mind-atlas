# Message Brokers: Kafka, RabbitMQ, SQS

[RabbitMQ](../../concepts/distributed-systems/messaging/rabbitmq.md), [Kafka](../../concepts/distributed-systems/messaging/kafka.md), Redis (used as a queue), and [SQS](../../concepts/distributed-systems/messaging/sqs.md) are all message queue / event-streaming systems used to decouple services in a distributed system — the same underlying problem covered in [Message Queues](../../concepts/distributed-systems/messaging/queues.md). This page compares the options and links out to a dedicated note for each; it doesn't re-describe any of them in full.

## The Core Four

| System | Type | Speed | Scale | Best Use |
|---|---|---|---|---|
| **[RabbitMQ](../../concepts/distributed-systems/messaging/rabbitmq.md)** | Message broker | Medium | Medium | Flexible routing, task-based pipelines |
| **[Kafka](../../concepts/distributed-systems/messaging/kafka.md)** | Event streaming | Very high | Huge | Big data / event systems, replayable history |
| **Redis Queue** ([lists](../../concepts/distributed-systems/messaging/redis-lists.md) / [BullMQ](../../concepts/distributed-systems/messaging/bullmq.md)) | In-memory queue | Very fast | Small–medium | Simple job queues |
| **[SQS](../../concepts/distributed-systems/messaging/sqs.md)** | Cloud queue | Medium | High | [AWS](../../concepts/cloud/infrastructure/aws.md)-native, fully managed serverless systems |

- **[RabbitMQ](../../concepts/distributed-systems/messaging/rabbitmq.md)** — a traditional broker with flexible exchange-based routing (fanout, direct, topic — see [Fan-Out Architecture](../../concepts/distributed-systems/patterns/fan-out-architecture.md)); reliable but not built for huge streaming scale.
- **[Kafka](../../concepts/distributed-systems/messaging/kafka.md)** — a distributed, partitioned, replayable log; extremely high throughput, but heavier to operate.
- **Redis Queue** — lightweight and in-memory, usually built on [Redis Lists](../../concepts/distributed-systems/messaging/redis-lists.md) directly or via [BullMQ](../../concepts/distributed-systems/messaging/bullmq.md) (Node.js) for retries/scheduling; not durable the way [Kafka](../../concepts/distributed-systems/messaging/kafka.md) is.
- **[SQS](../../concepts/distributed-systems/messaging/sqs.md)** — fully managed by [AWS](../../concepts/cloud/infrastructure/aws.md), no infrastructure to run, but ties you to the [AWS](../../concepts/cloud/infrastructure/aws.md) ecosystem and offers less routing flexibility than [RabbitMQ](../../concepts/distributed-systems/messaging/rabbitmq.md) or [Kafka](../../concepts/distributed-systems/messaging/kafka.md).

## Choosing for an AI Pipeline

For a multi-stage pipeline ([OCR](../../concepts/ai/ingestion/ocr.md) → chunking → [embeddings](../../concepts/ai/ingestion/embeddings.md) → clustering → [RAG](../../concepts/ai/rag/rag.md) → validation → output):

- **Simple / early-stage:** Redis queue.
- **Production, self-hosted:** [RabbitMQ](../../concepts/distributed-systems/messaging/rabbitmq.md) or [Kafka](../../concepts/distributed-systems/messaging/kafka.md), depending on throughput and replay needs.
- **Cloud-native / serverless:** [AWS SQS](../../concepts/distributed-systems/messaging/sqs.md).

**Senior-level summary:** [Message queues](../../concepts/distributed-systems/messaging/queues.md) like [RabbitMQ](../../concepts/distributed-systems/messaging/rabbitmq.md), [Kafka](../../concepts/distributed-systems/messaging/kafka.md), Redis, and [SQS](../../concepts/distributed-systems/messaging/sqs.md) decouple services in a distributed system, letting each pipeline stage run independently by passing messages instead of making direct calls. The choice depends on scale, durability, and infrastructure: Redis for simplicity, [RabbitMQ](../../concepts/distributed-systems/messaging/rabbitmq.md) for reliable task queues, [Kafka](../../concepts/distributed-systems/messaging/kafka.md) for large-scale streaming, and [SQS](../../concepts/distributed-systems/messaging/sqs.md) for fully managed cloud systems.

## Other Common Options

Beyond the four covered above, these show up often enough to recognize by name — each has its own dedicated note:

| System | Type | Notes |
|---|---|---|
| **[NATS](../../concepts/distributed-systems/messaging/nats.md) / [NATS](../../concepts/distributed-systems/messaging/nats.md) JetStream** | Lightweight messaging | Extremely low latency, simpler than Kafka; JetStream adds Kafka-like persistence/replay on top of core [NATS](../../concepts/distributed-systems/messaging/nats.md)'s fire-and-forget [pub/sub](../../concepts/distributed-systems/messaging/publish-subscribe.md) |
| **[Google Cloud Pub/Sub](../../concepts/distributed-systems/messaging/google-pubsub.md)** | Cloud event streaming | [GCP](../../concepts/cloud/infrastructure/gcp.md)'s fully-managed equivalent to [SQS](../../concepts/distributed-systems/messaging/sqs.md)/Kafka — a common default if already on [GCP](../../concepts/cloud/infrastructure/gcp.md) |
| **[Azure Service Bus](../../concepts/distributed-systems/messaging/azure-service-bus.md)** | Cloud message broker | [Azure](../../concepts/cloud/azure/azure.md)'s equivalent, with both queue and [pub/sub](../../concepts/distributed-systems/messaging/publish-subscribe.md) topic models |
| **[Celery](../../concepts/distributed-systems/messaging/celery.md)** | Task queue (Python) | The Python-ecosystem equivalent of [BullMQ](../../concepts/distributed-systems/messaging/bullmq.md) — built on top of a broker (commonly Redis or [RabbitMQ](../../concepts/distributed-systems/messaging/rabbitmq.md)), not a broker itself |
| **[ActiveMQ](../../concepts/distributed-systems/messaging/activemq.md)** | JMS message broker | Traditional, JVM/Java-standard broker — still common in enterprise/legacy environments |
| **[ZeroMQ](../../concepts/distributed-systems/messaging/zeromq.md)** | Messaging library | No broker process at all — sockets talk directly; application code takes on routing/persistence a broker would otherwise handle |

The pattern across nearly all of these: a **broker/queue** (a separate service coordinating messages) vs. a **task-queue library** ([Celery](../../concepts/distributed-systems/messaging/celery.md), [BullMQ](../../concepts/distributed-systems/messaging/bullmq.md) — built on top of a broker, adding job semantics like retries and scheduling) are two different layers, often confused because both get called "the queue" colloquially.

## Related

- [RabbitMQ](../../concepts/distributed-systems/messaging/rabbitmq.md)
- [Kafka](../../concepts/distributed-systems/messaging/kafka.md)
- [SQS](../../concepts/distributed-systems/messaging/sqs.md)
- [Message Queues](../../concepts/distributed-systems/messaging/queues.md)
- [Redis Lists](../../concepts/distributed-systems/messaging/redis-lists.md)
- [BullMQ](../../concepts/distributed-systems/messaging/bullmq.md)
- [NATS](../../concepts/distributed-systems/messaging/nats.md)
- [Google Cloud Pub/Sub](../../concepts/distributed-systems/messaging/google-pubsub.md)
- [Azure Service Bus](../../concepts/distributed-systems/messaging/azure-service-bus.md)
- [Celery](../../concepts/distributed-systems/messaging/celery.md)
- [ActiveMQ](../../concepts/distributed-systems/messaging/activemq.md)
- [ZeroMQ](../../concepts/distributed-systems/messaging/zeromq.md)
- [FIFO vs LIFO](../../concepts/distributed-systems/patterns/fifo-lifo.md)
- [Fan-Out Architecture](../../concepts/distributed-systems/patterns/fan-out-architecture.md)
- [Decouple Stages](../../concepts/distributed-systems/patterns/decouple-stages.md)
