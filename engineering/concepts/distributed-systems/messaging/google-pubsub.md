# Google Cloud Pub/Sub

Google Cloud's fully-managed, serverless messaging service — [GCP](../../cloud/infrastructure/gcp.md)'s answer to the same problem [AWS SQS/SNS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) and [Azure Service Bus](azure-service-bus.md) solve on their respective clouds. No servers to provision or scale; Google operates the entire message-storage/delivery layer.

## Core Concepts

| Term | Meaning |
|---|---|
| **Topic** | A named channel a publisher sends messages to |
| **Subscription** | A named "tap" on a topic that a consumer reads from — multiple subscriptions on one topic each get their own full copy of every message (fan-out by default) |
| **Push subscription** | [Pub/Sub](publish-subscribe.md) calls a webhook URL you provide for each message, rather than you polling for it |
| **Pull subscription** | Your consumer actively fetches messages, at its own pace |
| **Ack deadline** | How long a consumer has to acknowledge a message before [Pub/Sub](publish-subscribe.md) assumes it failed and redelivers it |

## Why Multiple Subscriptions Matter

Publishing once to a topic with three independent subscriptions means three independent consumers *each* receive every message — this is fan-out built into the primitive itself, not something bolted on. An `OrderCreated` topic could have one subscription feeding a fulfillment service, another feeding analytics, and a third feeding a notification service — each processes at its own pace, with its own ack deadline and retry behavior, entirely unaware of the others.

## Publishing (Node.js)

```javascript
const { PubSub } = require('@google-cloud/pubsub');
const pubsub = new PubSub();

const topic = pubsub.topic('orders-created');
await topic.publishMessage({ json: { orderId: 123 } });
```

## Pull Subscriber

```javascript
const subscription = pubsub.subscription('orders-created-fulfillment');

subscription.on('message', (message) => {
  console.log(JSON.parse(message.data.toString()));
  message.ack();  // must explicitly ack, or it's redelivered after the ack deadline
});

subscription.on('error', console.error);
```

## Common Questions

**What happens if a consumer never acks a message?**
> After the ack deadline passes, [Pub/Sub](publish-subscribe.md) assumes delivery failed and redelivers the message — meaning consumer code needs to handle duplicate delivery gracefully (the same "design for at-least-once, make handlers idempotent" principle as [BullMQ](bullmq.md) and most other queue/broker systems — see [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md)).

**When would push subscriptions be preferred over pull?**
> Push fits serverless consumers well (e.g. triggering a Cloud Function or Cloud Run service per message, with no long-running worker process to operate) — pull fits a traditional long-running worker that wants to control its own consumption rate and batching.

## Related

- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [Azure Service Bus](azure-service-bus.md)
- [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md)
