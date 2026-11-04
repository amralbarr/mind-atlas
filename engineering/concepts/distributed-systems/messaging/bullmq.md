# BullMQ

BullMQ is the standard Node.js/TypeScript job queue library built on [Redis](redis-lists.md) — the default choice mentioned across this vault's NestJS notes for offloading long-running work (AI processing, emails, image resizing) to a background worker instead of blocking a request. See [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) for how it compares to the heavier broker options.

## Core Concepts

| Term | Meaning |
|---|---|
| **Queue** | A named list of jobs waiting to be processed |
| **Job** | One unit of work — a name plus a [JSON](../../programming/fundamentals/json.md)-serializable payload |
| **Worker** | A process that pulls jobs off a queue and runs a handler function against each one |
| **Job state** | `waiting` → `active` → `completed` or `failed` (plus `delayed`, for jobs scheduled in the future) |

## Installation

```bash
npm install bullmq
```

Requires a running Redis instance — BullMQ uses Redis purely as its storage/coordination layer, not as application state.

## Adding a Job

```typescript
import { Queue } from 'bullmq';

const emailQueue = new Queue('emails', {
  connection: { host: 'localhost', port: 6379 },
});

await emailQueue.add('welcome-email', {
  userId: '123',
  email: 'user@example.com',
});
```

## Processing Jobs

```typescript
import { Worker } from 'bullmq';

const worker = new Worker(
  'emails',
  async (job) => {
    console.log(`Sending ${job.name} to ${job.data.email}`);
    // ... actual send logic
  },
  { connection: { host: 'localhost', port: 6379 } },
);

worker.on('completed', (job) => console.log(`${job.id} done`));
worker.on('failed', (job, err) => console.error(`${job?.id} failed:`, err));
```

The queue (producer side) and worker (consumer side) are deliberately separate — a web server process can `add()` jobs without ever running a `Worker`, while a separate background process runs one or more workers, scaling independently of the web tier.

## Retries & Backoff

```typescript
await emailQueue.add('welcome-email', data, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 1000 }, // 1s, 2s, 4s between retries
});
```

A job that throws inside its handler is automatically retried up to `attempts` times before landing in the `failed` state — this is what makes BullMQ suitable for work that talks to flaky external services (an AI API, a third-party webhook) without hand-rolling retry logic in every handler.

## Delayed & Repeatable Jobs

```typescript
// Run once, 10 minutes from now
await queue.add('reminder', data, { delay: 10 * 60 * 1000 });

// Run on a recurring schedule (cron syntax)
await queue.add('daily-report', {}, { repeat: { pattern: '0 9 * * *' } });
```

## Concurrency & Rate Limiting

```typescript
const worker = new Worker('emails', handler, {
  connection,
  concurrency: 5,              // process up to 5 jobs at once, per worker process
  limiter: { max: 100, duration: 60_000 },  // never exceed 100 jobs/minute total
});
```

`concurrency` controls parallelism per worker process; `limiter` caps total throughput across all jobs the queue processes — this matters most when each job calls a rate-limited or metered external API (an AI inference endpoint, a third-party service with its own quota), where exceeding the limit costs money or gets the whole queue throttled/banned upstream.

## NestJS Integration

```typescript
// module
BullModule.registerQueue({ name: 'emails' });

// producer (in a service)
constructor(@InjectQueue('emails') private emailQueue: Queue) {}

// consumer
@Processor('emails')
export class EmailProcessor extends WorkerHost {
  async process(job: Job): Promise<void> {
    // handle job.data
  }
}
```

## Common Questions

**When is BullMQ the wrong choice, compared to [Kafka](kafka.md) or [RabbitMQ](rabbitmq.md)?**
> BullMQ is built for job/task processing (a finite unit of work with a clear success/fail outcome), not high-throughput event streaming or guaranteed multi-consumer fan-out at [Kafka](kafka.md)'s scale. See [Message Brokers](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) for the fuller comparison — BullMQ trades [Kafka](kafka.md)'s durability/replay guarantees for much simpler setup and very low latency.

**Does BullMQ guarantee a job runs exactly once?**
> No system guarantees pure exactly-once delivery in the general case — BullMQ guarantees **at-least-once** by default (a job that fails or whose worker crashes mid-processing gets retried), which means handlers should be written to be [idempotent](../../programming/fundamentals/idempotency-and-race-conditions.md) wherever the underlying action isn't naturally safe to repeat (e.g. use an [idempotency](../../backend/api/idempotency.md) key before charging a payment twice).

## Related

- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [Redis Lists](redis-lists.md)
- [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md)
- [NestJS Overview](../../backend/nestjs/nestjs-overview.md)
