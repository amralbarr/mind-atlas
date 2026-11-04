# Publish-Subscribe (Pub/Sub)

**Publish-Subscribe** is a messaging pattern where senders (**publishers**) don't send messages to specific receivers at all — they publish messages to a named **topic** (or **channel**), and any number of **subscribers** who've registered interest in that topic receive a copy, without the publisher knowing or caring who (or how many) is listening.

```text
Publisher → Topic "orders.created" → Subscriber A (email service)
                                    → Subscriber B (analytics service)
                                    → Subscriber C (inventory service)
```

## The Defining Property: Publishers and Subscribers Don't Know About Each Other

This is what separates pub/sub from a normal function call or a direct API request — the publisher has no reference to, and no dependency on, whatever ends up consuming the message. Subscribers can be added or removed at runtime without the publisher's code changing at all; a new service can start listening to `orders.created` tomorrow without anyone touching the code that publishes it today.

## Pub/Sub vs. Point-to-Point Queues

This is the most common point of confusion, since both use a broker in the middle:

| | Point-to-point (queue) | Publish-Subscribe |
|---|---|---|
| Delivery | Exactly **one** consumer gets each message (competing consumers share the load) | **Every** current subscriber gets its own copy of each message |
| Shape | Work distribution — spread tasks across a worker pool | Broadcast — notify everyone interested that something happened |
| Adding a consumer | Increases throughput (more workers share the same work) | Doesn't change what existing subscribers receive — it's a fully independent new copy-recipient |

Concretely: a job queue where five workers each `pop` a job is point-to-point (each job is processed once, by one worker). A topic where five services each independently react to the same `UserSignedUp` event is pub/sub (each service processes every event).

Many real systems support both models side by side — see the JMS Queue vs. Topic distinction in [ActiveMQ](activemq.md), or [Azure Service Bus](azure-service-bus.md)'s queues (point-to-point) vs. topics+subscriptions (pub/sub).

## Pub/Sub vs. Fan-Out

Closely related but not identical: [Fan-Out Architecture](../patterns/fan-out-architecture.md) describes the *outcome* — one event reaching many independent consumers in parallel — while pub/sub describes a specific *mechanism* for achieving it, built around named topics and a subscriber registration step. A fanout exchange in [RabbitMQ](rabbitmq.md) is one concrete implementation of fan-out; publishing to a topic that multiple services subscribe to is another. In practice the two terms overlap heavily and are often used interchangeably, but pub/sub specifically implies the topic/subscription vocabulary and the ability for subscribers to come and go independently of the publisher.

## Delivery Guarantees Vary Widely by Implementation

"Pub/sub" describes the *pattern*, not a specific durability guarantee — this varies a lot by system:

| System | What happens to a message if no one's subscribed when it's published |
|---|---|
| **Redis Pub/Sub** (native `PUBLISH`/`SUBSCRIBE`) | Lost — fire-and-forget, no persistence, no history for a late subscriber |
| **Core [NATS](nats.md)** | Lost — same fire-and-forget model; [NATS](nats.md) **JetStream** adds persistence on top |
| **[Google Cloud Pub/Sub](google-pubsub.md)** | Retained — a subscription created before publish will still receive it even if the subscriber wasn't actively connected at that instant |
| **[Kafka](kafka.md) topics** (see [Message Brokers](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)) | Retained as a durable, replayable log — a new consumer group can read from the beginning |

Before choosing an implementation, be explicit about whether "a subscriber that wasn't listening at the moment of publish should still eventually get the message" is a requirement — that answer alone rules out or requires specific systems.

## Example: Redis Pub/Sub

```javascript
// Subscriber
const sub = redis.duplicate();
await sub.subscribe('orders.created', (message) => {
  console.log('New order:', JSON.parse(message));
});

// Publisher — has no idea who (if anyone) is subscribed
await redis.publish('orders.created', JSON.stringify({ orderId: 123 }));
```

If no process is subscribed to `orders.created` at the moment `publish` runs, the message is simply gone — a good illustration of why "which pub/sub implementation" is itself a load-bearing decision, not an interchangeable detail.

## Common Questions

**Is a webhook a form of pub/sub?**
> Not quite — a webhook is still point-to-point (the sender explicitly knows the receiving URL) and typically one-to-one, whereas pub/sub's defining trait is that the publisher doesn't address any specific receiver at all. A webhook *fan-out* system (one event triggering calls to many registered webhook URLs) gets closer to pub/sub in spirit, though the mechanism (direct [HTTP](../../networking/http.md) calls vs. a broker-mediated topic) is different.

**Why would a system choose [Kafka](kafka.md)'s persistent topic model over lightweight Redis Pub/Sub?**
> It comes down to that delivery-guarantee question above: Redis Pub/Sub is simpler and faster but loses anything published while a subscriber is offline; [Kafka](kafka.md) retains messages so late or restarted consumers can catch up — at the cost of running a heavier system. See [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) for the fuller trade-off.

## Related

- [Fan-Out Architecture](../patterns/fan-out-architecture.md)
- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [NATS](nats.md)
- [Google Cloud Pub/Sub](google-pubsub.md)
- [Azure Service Bus](azure-service-bus.md)
- [ActiveMQ](activemq.md)
- [Redis Lists](redis-lists.md)
- [Message Queues](queues.md)
- [Webhooks](../../backend/api/webhooks.md)
