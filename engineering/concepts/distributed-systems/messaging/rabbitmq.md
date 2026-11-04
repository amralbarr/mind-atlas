# RabbitMQ

RabbitMQ is a traditional, general-purpose [message broker](queues.md) — a separate server process that receives messages from producers, routes them according to rules you configure, and holds them in queues until a consumer is ready to process them. See [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) for how it compares to the other options.

## Core Concepts

| Term | Meaning |
|---|---|
| **Queue** | A buffer holding messages until a consumer pulls them off |
| **Exchange** | The routing layer a producer actually publishes to — it decides which queue(s) a message lands in based on the exchange type and a routing key |
| **Binding** | A rule connecting an exchange to a queue (optionally filtered by routing key/pattern) |
| **Routing key** | A string attached to a message, matched against bindings to decide where it goes |
| **Acknowledgement (ack)** | A consumer's explicit signal that a message was processed successfully — an unacked message is redelivered if the consumer disconnects |

Producers never publish directly to a queue — they always publish to an **exchange**, which is what makes RabbitMQ's routing flexible instead of a single unavoidable point-to-point pipe.

## Exchange Types

| Type | Routing behavior |
|---|---|
| **Direct** | Delivers to queues whose binding key exactly matches the message's routing key |
| **Fanout** | Delivers to every queue bound to the exchange, ignoring the routing key entirely — the basis of [fan-out architecture](../patterns/fan-out-architecture.md) |
| **Topic** | Matches routing keys against wildcard patterns (`orders.*`, `orders.#`) — the most flexible type |
| **Headers** | Routes based on message header values instead of the routing key (rarely used) |

## Running It (Docker)

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

`15672` exposes the web management UI (`http://localhost:15672`, default guest/guest on `localhost` only); `5672` is the AMQP port clients actually connect to.

## Publishing and Consuming (Node.js)

```javascript
const amqp = require('amqplib');

const conn = await amqp.connect('amqp://localhost');
const channel = await conn.createChannel();

await channel.assertExchange('orders', 'topic', { durable: true });
await channel.assertQueue('orders.fulfillment', { durable: true });
await channel.bindQueue('orders.fulfillment', 'orders', 'orders.created.*');

// Publisher
channel.publish('orders', 'orders.created.us', Buffer.from(JSON.stringify({ orderId: 123 })), {
  persistent: true, // survives a broker restart, combined with a durable queue
});

// Consumer
channel.consume('orders.fulfillment', (msg) => {
  console.log(JSON.parse(msg.content.toString()));
  channel.ack(msg); // without this, the message is redelivered on disconnect
});
```

## Dead Letter Queues

A message that's rejected, expires, or exceeds a retry limit can be automatically routed to a **dead letter exchange (DLX)** instead of being silently dropped or endlessly retried:

```javascript
await channel.assertQueue('orders.fulfillment', {
  durable: true,
  arguments: { 'x-dead-letter-exchange': 'orders.dlx' },
});
```

This turns "a message nobody could process" into something inspectable, rather than a silent loss.

## Common Questions

**Does RabbitMQ guarantee message ordering?**
> Only within a single queue with a single consumer — multiple consumers on the same queue process messages in parallel, so global ordering isn't guaranteed unless you deliberately route related messages (e.g. everything for one order) to the same queue via a consistent routing key.

**When does RabbitMQ stop being the right choice?**
> When the workload is really high-throughput event streaming that multiple independent consumer groups need to replay from history — that's [Kafka's](kafka.md) core strength, not RabbitMQ's. RabbitMQ shines at flexible routing and reliable task delivery, not at retaining a durable, replayable log of everything that ever happened.

## Related

- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [Kafka](kafka.md)
- [Queues](queues.md)
- [Fan-Out Architecture](../patterns/fan-out-architecture.md)
- [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md)
- [Dead-Letter Queue](dead-letter-queue.md)
- [Backpressure](../patterns/backpressure.md)
