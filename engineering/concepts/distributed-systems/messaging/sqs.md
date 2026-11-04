# AWS SQS

Amazon Simple Queue Service (SQS) is [AWS](../../cloud/infrastructure/aws.md)'s fully managed message queue — there's no broker to install, patch, or scale; you create a queue via the API/console and [AWS](../../cloud/infrastructure/aws.md) operates the underlying infrastructure. See [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) for how it compares to the self-hosted options.

## Core Concepts

| Term | Meaning |
|---|---|
| **Standard queue** | At-least-once delivery, best-effort ordering, nearly unlimited throughput — the default queue type |
| **FIFO queue** | Strict ordering and exactly-once processing *within a message group*, at lower throughput than a standard queue — see [FIFO vs. LIFO](../patterns/fifo-lifo.md) |
| **Visibility timeout** | How long a message is hidden from other consumers after being received, before it reappears if not deleted — the mechanism that prevents two workers from processing the same message concurrently |
| **[Dead-letter queue](dead-letter-queue.md) (DLQ)** | A separate queue a message is moved to after failing processing a configured number of times, instead of retrying forever |
| **Long polling** | Consumers wait up to 20s for a message rather than repeatedly polling an empty queue — reduces empty-response API calls and cost |

## Creating a Queue and Sending a Message (AWS CLI)

```bash
aws sqs create-queue --queue-name orders-queue

aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/orders-queue \
  --message-body '{"orderId": 123}'
```

## Producing and Consuming (Node.js, AWS SDK v3)

```javascript
import { SQSClient, SendMessageCommand, ReceiveMessageCommand, DeleteMessageCommand } from '@aws-sdk/client-sqs';

const sqs = new SQSClient({ region: 'us-east-1' });
const queueUrl = 'https://sqs.us-east-1.amazonaws.com/123456789012/orders-queue';

// Send
await sqs.send(new SendMessageCommand({
  QueueUrl: queueUrl,
  MessageBody: JSON.stringify({ orderId: 123 }),
}));

// Receive (long polling) and delete on success
const { Messages } = await sqs.send(new ReceiveMessageCommand({
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 10,
  WaitTimeSeconds: 20,
}));

for (const msg of Messages ?? []) {
  console.log(JSON.parse(msg.Body));
  // Must explicitly delete — SQS doesn't know processing succeeded otherwise
  await sqs.send(new DeleteMessageCommand({ QueueUrl: queueUrl, ReceiptHandle: msg.ReceiptHandle }));
}
```

Failing to delete a message after successful processing means it becomes visible again once the visibility timeout expires and gets redelivered — this is *why* consumers must be [idempotent](../../programming/fundamentals/idempotency-and-race-conditions.md), the same principle as every other at-least-once system.

## Serverless Consumption (Lambda Trigger)

A common pattern is skipping manual polling entirely by wiring a Lambda function directly as the queue's consumer — [AWS](../../cloud/infrastructure/aws.md) invokes the function automatically as messages arrive, batching multiple messages per invocation, and handles the receive/delete/visibility-timeout mechanics for you.

## Common Questions

**When is SQS FIFO worth the throughput cost over standard?**
> When strict ordering and exactly-once processing actually matter for correctness — e.g. sequential state transitions for one entity (an order's status must go `created → paid → shipped` in order). If occasional out-of-order delivery or duplicate processing (handled via [idempotency](../../backend/api/idempotency.md)) is acceptable, standard queues are cheaper and scale further.

**How does SQS compare to [Kafka](kafka.md) for an [AWS](../../cloud/infrastructure/aws.md)-native system?**
> SQS is a simple, fully managed queue — not a durable, replayable event log. If a system needs multiple independent consumers to each read the full history of every event (event sourcing, analytics replay), that's [Kafka's](kafka.md) job, or [AWS](../../cloud/infrastructure/aws.md)'s own equivalent, Kinesis — SQS is built for decoupling producers from consumers of discrete work items, not for stream replay.

## Related

- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [FIFO vs. LIFO](../patterns/fifo-lifo.md)
- [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md)
- [AWS](../../cloud/infrastructure/aws.md)
- [Dead-Letter Queue](dead-letter-queue.md)
