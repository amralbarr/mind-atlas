# NATS

NATS is a lightweight, high-performance messaging system built around simplicity — a single small binary, sub-millisecond latency, and a [pub/sub](publish-subscribe.md) model that's deliberately much simpler to operate than [Kafka](kafka.md). See [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) for how it compares to the heavier options.

## Core NATS vs. JetStream

| | Core NATS | JetStream |
|---|---|---|
| Delivery | Fire-and-forget — if no subscriber is listening, the message is gone | Persistent — messages are stored and can be replayed |
| Durability | None | Configurable retention (time, size, or message count) |
| Use case | Real-time signals where losing a message during a brief outage is acceptable | Anything needing [Kafka](kafka.md)-like durability/replay, without [Kafka](kafka.md)'s operational weight |

Core NATS alone is closer to a live radio broadcast — tune in or miss it; JetStream adds a recording you can rewind, layered on the same simple transport.

## Basic Pub/Sub

```javascript
import { connect, StringCodec } from 'nats';

const nc = await connect({ servers: 'localhost:4222' });
const sc = StringCodec();

// Subscriber
const sub = nc.subscribe('orders.created');
(async () => {
  for await (const msg of sub) {
    console.log(sc.decode(msg.data));
  }
})();

// Publisher
nc.publish('orders.created', sc.encode(JSON.stringify({ orderId: 123 })));
```

## Request-Reply (Built In)

Unlike most brokers, NATS has request-reply as a first-class primitive, not something bolted on with correlation ids and a reply queue:

```javascript
const response = await nc.request('user.get', sc.encode('user-1'), { timeout: 1000 });
console.log(sc.decode(response.data));
```

This makes NATS a reasonable lightweight alternative to [gRPC](../patterns/network-communication.md) or [REST](../../backend/api/rest.md) for internal service-to-service calls, when the simplicity of "publish a subject, get a reply" outweighs [gRPC](../../backend/api/grpc.md)'s strong typing/codegen.

## Subjects & Wildcards

NATS routes messages by **subject** (a dot-separated string, not a queue name) with wildcard subscription support:

```text
orders.created
orders.*        matches orders.created, orders.updated, orders.cancelled — one level
orders.>        matches orders.created, orders.eu.created, ...          — any depth
```

## Common Questions

**Why choose NATS over [Kafka](kafka.md) for an event-driven system?**
> When operational simplicity and latency matter more than [Kafka](kafka.md)'s massive-scale durability/replay guarantees — a single NATS binary with no external dependencies (JetStream adds its own storage, but still far lighter than a [Kafka](kafka.md)+ZooKeeper/KRaft cluster) is much faster to stand up and reason about for small-to-medium systems.

**Is JetStream a separate product from NATS?**
> No — it's an optional persistence layer built into the same NATS server, enabled per-subject/stream rather than being a different system to deploy and operate.

## Related

- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [Network Communication](../patterns/network-communication.md)
- [Queues](queues.md)
- [Consensus Algorithms (Raft & Paxos)](../patterns/consensus-algorithms.md) — JetStream clustering
