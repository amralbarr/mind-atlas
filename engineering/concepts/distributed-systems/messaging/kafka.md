# Apache Kafka

Kafka is a distributed event-streaming platform built around a durable, append-only, replayable log rather than a transient queue — messages aren't removed once consumed, they simply age out based on a retention policy, so any consumer can re-read history independently. See [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) for how it compares to the other options.

## Core Concepts

| Term | Meaning |
|---|---|
| **Topic** | A named, append-only log that producers write to and consumers read from |
| **Partition** | A topic is split into one or more ordered, independent partitions — the unit of parallelism and the only place strict ordering is guaranteed |
| **Offset** | A message's position within its partition — consumers track their own offset instead of the broker deleting a message once it's read |
| **Broker** | One server in a Kafka cluster, holding a subset of partitions |
| **Consumer group** | A set of consumers that split a topic's partitions between them — each partition is read by exactly one consumer within a group, but every group gets its own full copy of the stream |
| **Replication factor** | How many brokers hold a copy of each partition, for fault tolerance if a broker goes down |

## Why Partitions Matter for Ordering

Kafka only guarantees message order **within a single partition**, not across an entire topic. Messages are assigned to a partition by key (commonly hashed), so sending every message for one entity (e.g. one `orderId`) with the same key guarantees they land in the same partition and are processed in order relative to each other — but two different orders can be processed out of order relative to one another, on different partitions, in parallel.

```text
Topic: orders (3 partitions)
  Partition 0: order-1 msg1 → order-1 msg2 → order-4 msg1   (in order)
  Partition 1: order-2 msg1 → order-2 msg2                  (in order)
  Partition 2: order-3 msg1
```

## Running It (Docker, KRaft mode — no ZooKeeper)

```bash
docker run -d --name kafka -p 9092:9092 \
  -e KAFKA_NODE_ID=1 \
  -e KAFKA_PROCESS_ROLES=broker,controller \
  -e KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 \
  -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  apache/kafka:latest
```

Kafka has run in **KRaft mode** (its own built-in consensus, replacing ZooKeeper) as the default since Kafka 3.5+ — a meaningfully lighter operational footprint than the ZooKeeper-dependent clusters common in older deployments.

## Producing and Consuming (Node.js, kafkajs)

```javascript
const { Kafka } = require('kafkajs');
const kafka = new Kafka({ brokers: ['localhost:9092'] });

// Producer
const producer = kafka.producer();
await producer.connect();
await producer.send({
  topic: 'orders',
  messages: [{ key: 'order-123', value: JSON.stringify({ orderId: 123, status: 'created' }) }],
});

// Consumer (part of a consumer group)
const consumer = kafka.consumer({ groupId: 'fulfillment-service' });
await consumer.connect();
await consumer.subscribe({ topic: 'orders', fromBeginning: false });

await consumer.run({
  eachMessage: async ({ partition, message }) => {
    console.log(partition, message.offset, JSON.parse(message.value.toString()));
  },
});
```

## Replay

Because Kafka doesn't delete a message on consumption, a brand-new consumer group (or a group deliberately reset) can re-read a topic's full retained history from the beginning:

```javascript
await consumer.subscribe({ topic: 'orders', fromBeginning: true });
```

This is the capability that makes Kafka a natural fit for event sourcing and rebuilding downstream state from scratch, which a transient queue like [RabbitMQ](rabbitmq.md) or [SQS](sqs.md) can't offer once a message has been acked and removed.

## Common Questions

**Why is Kafka considered harder to operate than [RabbitMQ](rabbitmq.md)?**
> Running a real Kafka cluster well means reasoning about partition counts (set at topic creation, expensive to change later), replication, consumer group rebalancing, and retention/compaction policies — none of which a [RabbitMQ](rabbitmq.md) deployment has to think about. That operational weight is the tradeoff for Kafka's throughput and replay guarantees.

**What happens if a consumer group has more consumers than partitions?**
> The extra consumers sit idle — a partition is only ever assigned to one consumer within a group at a time, so parallelism within a group is capped by the topic's partition count, which is why partition count is chosen with expected consumer scale in mind.

## Related

- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [RabbitMQ](rabbitmq.md)
- [Queues](queues.md)
- [Distributed Databases](../../databases/distributed/distributed-databases.md)
- [Consensus Algorithms (Raft & Paxos)](../patterns/consensus-algorithms.md) — KRaft mode
- [Backpressure](../patterns/backpressure.md)
