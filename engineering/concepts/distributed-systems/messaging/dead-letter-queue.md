# Dead-Letter Queue (DLQ)

A dead-letter queue is a separate holding queue that a broker or consumer routes a message to when it can't be processed successfully after repeated attempts — instead of retrying forever, silently dropping it, or letting one bad message block every message behind it.

## The Problem It Solves

Without a DLQ, a message that can never succeed (a malformed payload, a reference to data that was since deleted, a bug in the consumer that always throws on this specific input) has only two bad outcomes:

```text
Option A: retry forever
  → the message blocks the queue (or keeps consuming resources) indefinitely,
    and everything behind it in a FIFO queue may be stuck waiting

Option B: give up silently and discard it
  → the failure is invisible — nobody knows an order/payment/notification
    was silently lost
```

A DLQ gives a third option: after a bounded number of retries, move the message somewhere inspectable, and let the main queue keep flowing.

## The Standard Flow

```text
Producer → Queue → Consumer
                       │
                       ├─ success → ack, done
                       │
                       └─ failure (repeated past max retries)
                                       ↓
                              Dead-Letter Queue
                                       ↓
                          (alert, manual inspection, reprocessing)
```

## Configuring a DLQ (RabbitMQ)

```javascript
await channel.assertExchange('orders.dlx', 'fanout', { durable: true });
await channel.assertQueue('orders.dlq', { durable: true });
await channel.bindQueue('orders.dlq', 'orders.dlx', '');

await channel.assertQueue('orders.fulfillment', {
  durable: true,
  arguments: {
    'x-dead-letter-exchange': 'orders.dlx',
    'x-message-ttl': 60000,        // messages older than 60s are dead-lettered
    'x-delivery-limit': 5,          // (quorum queues) max redelivery attempts
  },
});
```

A message lands in the DLQ when it's explicitly rejected (`channel.nack(msg, false, false)` — don't requeue), when it expires (TTL), or when it exceeds a configured retry/delivery limit, depending on which of these triggers the broker supports and which are configured.

## Configuring a DLQ (AWS SQS)

```json
{
  "RedrivePolicy": {
    "deadLetterTargetArn": "arn:aws:sqs:us-east-1:123456789012:orders-dlq",
    "maxReceiveCount": 5
  }
}
```

After a message has been received (and not deleted, meaning processing failed) 5 times, [SQS](sqs.md) automatically moves it to `orders-dlq` instead of redelivering it a sixth time.

## Why "Retry, Then Dead-Letter" (Not Immediate Dead-Lettering)

Most failures are transient — a downstream service briefly down, a database connection blip, a momentary network partition — and would succeed on a retry a few seconds later. Sending a message to the DLQ on the very first failure would flood it with messages that were never actually broken, just unlucky in timing. The standard pattern is:

```text
Attempt 1 fails → retry with backoff
Attempt 2 fails → retry with backoff
Attempt 3 fails → retry with backoff
Attempt N fails → give up, dead-letter it
```

Exponential backoff between attempts (1s, 2s, 4s, 8s...) gives transient issues time to resolve before escalating a message to "needs a human/reprocessing," while still bounding how long a genuinely broken message can occupy the main queue.

## What Happens to a Message Once It's Dead-Lettered

A DLQ is a *destination*, not an *end state* — the message still needs a resolution path:

| Approach | When it's appropriate |
|---|---|
| **Alert + manual inspection** | Low-volume, high-value messages (a failed payment) where a human should look at exactly what went wrong |
| **Automatic reprocessing after a fix** | Once the root cause (a bug, a bad deploy) is fixed, replay the DLQ's contents back into the main queue |
| **Log and discard** | Genuinely unrecoverable/invalid messages (malformed data from a buggy upstream that's since been fixed) where reprocessing would never succeed anyway |

Leaving messages to accumulate in a DLQ with no monitoring or resolution process defeats the entire purpose — a DLQ without alerting is just a slower, quieter way to lose data.

## Where DLQs Show Up Across Brokers

| Broker | DLQ mechanism |
|---|---|
| [RabbitMQ](rabbitmq.md) | Dead-letter exchange (DLX), configured per-queue via `x-dead-letter-exchange` |
| [SQS](sqs.md) | A separate queue configured as the target of a redrive policy |
| [Azure Service Bus](azure-service-bus.md) | A built-in, automatic sub-queue (`<queue>/$DeadLetterQueue`) attached to every queue/subscription |
| [Kafka](kafka.md) | No built-in DLQ concept — typically implemented at the application/consumer level by publishing failed messages to a separate "dead letter" topic, since [Kafka](kafka.md)'s log-based model doesn't have per-message ack/reject semantics the way a traditional queue does |

## Common Questions

**Is a DLQ the same thing as a retry queue?**
> No, though they're often used together — a retry queue holds messages that are still expected to eventually succeed (often with a delay before redelivery); a DLQ holds messages that have exhausted their retries and need a different resolution path (human inspection, a code fix, or deliberate discard).

**Does every message that fails once need to end up in a DLQ eventually?**
> No — the vast majority of failures should resolve via retry (transient network/service issues). A DLQ should be the exception path for messages that persistently fail across multiple attempts, not the default outcome of any single failure.

**Why doesn't [Kafka](kafka.md) have a built-in DLQ like [RabbitMQ](rabbitmq.md) or [SQS](sqs.md)?**
> [Kafka](kafka.md)'s consumption model is pull-based and offset-tracked rather than ack/reject-per-message — a consumer just advances its offset once it's "done" with a batch, with no native concept of rejecting one specific message back to the broker. Handling a poison message in [Kafka](kafka.md) is the consuming application's responsibility, typically by catching the processing failure and explicitly producing that message onto a separate dead-letter topic itself.

## Related

- [RabbitMQ](rabbitmq.md)
- [SQS](sqs.md)
- [Azure Service Bus](azure-service-bus.md)
- [Kafka](kafka.md)
- [Backpressure](../patterns/backpressure.md)
- [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md)
- [Exponential Backoff and Jitter](../../backend/resilience/exponential-backoff-and-jitter.md) — the retry strategy exhausted before a message lands here
