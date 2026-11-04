# Azure Service Bus

[Microsoft Azure](../../cloud/azure/azure.md)'s fully-managed enterprise messaging service — supports both simple point-to-point queues and [pub/sub](publish-subscribe.md)-style topics in one product, making it more of an "either model, your choice" service than [Google Pub/Sub](google-pubsub.md) (topics-and-subscriptions only) or plain [SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) (queues only). See [Azure](../cloud/azure.md) for the broader [Azure](../../cloud/azure/azure.md) platform context.

## Two Models in One Service

| Model | Shape | Use when |
|---|---|---|
| **Queue** | One producer side, one logical consumer side (competing consumers can share load) | Simple task distribution — each message processed by exactly one consumer instance |
| **Topic + Subscriptions** | One producer, many independent subscriptions, each receiving its own copy | Fan-out — multiple independent consumers each need every message (analytics + fulfillment + notifications, from one event) |

## Queue Example (Node.js)

```javascript
const { ServiceBusClient } = require('@azure/service-bus');

const client = new ServiceBusClient(connectionString);
const sender = client.createSender('orders-queue');

await sender.sendMessages({ body: { orderId: 123 } });

const receiver = client.createReceiver('orders-queue');
receiver.subscribe({
  processMessage: async (message) => {
    console.log(message.body);
    await receiver.completeMessage(message);  // ack — removes it from the queue
  },
  processError: async (err) => console.error(err),
});
```

## Topics & Subscription Filters

A distinguishing Service Bus feature: **subscription filters** let each subscription receive only a subset of a topic's messages, based on message properties — without the publisher needing to know or care who's filtering for what:

```javascript
// Only messages where the "region" property equals "EU" reach this subscription
await adminClient.createRule('orders-topic', 'eu-orders-sub', {
  filter: { sqlExpression: "region = 'EU'" },
});
```

This is closer to a lightweight content-based routing layer than plain topic fan-out — each subscription can effectively define its own slice of the stream.

## Dead-Letter Queue (Built In)

Every queue and subscription automatically has an associated dead-letter sub-queue — a message that repeatedly fails processing (or exceeds a max delivery count) is moved there automatically rather than being lost or endlessly retried, giving operators a place to inspect and manually reprocess failures.

## Common Questions

**How does this compare to using plain [Azure](../../cloud/azure/azure.md) Storage [Queues](queues.md) instead?**
> Storage [Queues](queues.md) are simpler and cheaper but lack Service Bus's topics/subscriptions, filters, and richer delivery guarantees (like sessions for ordered processing) — Storage Queues fit basic task-queue needs, Service Bus fits scenarios needing [pub/sub](publish-subscribe.md) fan-out or more advanced routing.

**Does Service Bus guarantee ordering?**
> Only within a **session** — messages sent with the same `sessionId` are guaranteed to be processed in order by a session-aware receiver; without sessions, ordering across the queue/subscription as a whole isn't guaranteed under concurrent consumption.

## Related

- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [Google Cloud Pub/Sub](google-pubsub.md)
- [Azure](../cloud/azure.md)
- [Dead-Letter Queue](dead-letter-queue.md)
