# Backpressure

Backpressure is what happens — and what a well-designed system deliberately does — when a consumer can't keep up with the rate a producer is sending data, and that slowdown needs to propagate backward through the pipeline instead of silently piling up (or falling over) at the overwhelmed stage.

## The Problem Without Backpressure

```text
Producer: sends 10,000 events/sec
Consumer: can only process 1,000 events/sec
```

If nothing pushes back, the gap between production and consumption has to go *somewhere*:

- **Unbounded queue growth** — events pile up in memory until the process runs out of RAM and crashes, taking down in-flight work with it.
- **Silent data loss** — a queue with no room drops new events rather than rejecting them loudly, and nobody notices until the data is already gone.
- **Cascading failure** — an overwhelmed consumer becomes slow to respond to *everything*, including health checks, causing upstream systems (like a load balancer) to make bad decisions based on stale state.

Backpressure is the deliberate mechanism that prevents all three by making the slowdown visible and controllable instead of an invisible time bomb.

## The Core Mechanisms

| Mechanism | How it works |
|---|---|
| **Bounded queues/buffers** | Cap the queue size; once full, either block the producer or reject new items explicitly — an unbounded queue just delays the crash, it doesn't prevent it |
| **Blocking the producer** | The producer's `send`/`write` call blocks until the consumer has room — the simplest form of backpressure, common in in-process pipelines (e.g. Node.js streams' `write()` returning `false` when the internal buffer is full) |
| **Explicit signaling (pull-based)** | The consumer requests more data when ready, rather than the producer pushing continuously — reactive streams (RxJS, Reactive Streams spec) formalize this as the consumer calling `request(n)` |
| **[Rate limiting](../../backend/architecture/rate-limiting.md) the producer** | The producer is told (or infers, e.g. from repeated `429`s) to slow its send rate — see [Rate Limiting](../../backend/architecture/rate-limiting.md) for the receiving side of this same coordination |
| **Load shedding** | When backpressure alone isn't enough, deliberately drop lower-priority work rather than let everything degrade together — e.g. rejecting new requests outright once a queue depth threshold is crossed, so already-accepted work can still complete |

## Backpressure in Node.js Streams

A concrete, everyday example: piping a large file to a slow destination.

```javascript
const readStream = fs.createReadStream('huge-file.csv');
const writeStream = fs.createWriteStream('output.csv');

readStream.on('data', (chunk) => {
  const canContinue = writeStream.write(chunk);
  if (!canContinue) {
    readStream.pause();               // stop reading — the writer's buffer is full
    writeStream.once('drain', () => readStream.resume()); // resume once it's drained
  }
});
```

`.write()` returning `false` **is** backpressure — the writable stream is explicitly signaling "I'm full, stop sending until I fire `drain`." `.pipe()` handles exactly this pause/resume dance automatically, which is the main reason to prefer it over manual `data`/`write` wiring.

## Backpressure in Message Queues

A [queue](../messaging/queues.md)/broker is itself a backpressure buffer between producer and consumer — but only up to its own configured limits:

- **[RabbitMQ](../messaging/rabbitmq.md)** — consumer acknowledgment plus a configurable **prefetch count** limits how many unacknowledged messages a consumer can be handed at once, preventing a slow consumer from being flooded faster than it can process.
- **[Kafka](../messaging/kafka.md)** — consumers pull at their own pace (rather than the broker pushing), which is itself a natural backpressure mechanism; a slow consumer simply falls further behind in the log without the broker force-feeding it.
- **A queue with no depth limit** — defers the problem rather than solving it; eventually the broker itself runs out of memory/disk, which is why production queue configs almost always cap max queue length or enable disk-backed overflow with alerting.

## Backpressure vs. Rate Limiting vs. Dead-Lettering

These three are commonly discussed together because they all deal with "too much, too fast," but they solve it differently:

| | Backpressure | [Rate Limiting](../../backend/architecture/rate-limiting.md) | [Dead-Letter Queue](../messaging/dead-letter-queue.md) |
|---|---|---|---|
| Deals with | A capacity mismatch between producer and consumer speed | A client sending more requests than allowed | A specific message that repeatedly fails to process |
| Response | Slow the producer down / signal "not yet" | Reject the request outright (often with a client-facing error) | Move the poison message aside so it stops blocking everything else |
| Direction | Internal, between pipeline stages | Client-facing, at the edge of a system | Internal, within one consumer's processing of one queue |

## Common Questions

**Isn't an unbounded queue a simple way to "solve" a speed mismatch?**
> It defers the problem rather than solving it — memory isn't infinite, so an unbounded queue just delays the eventual crash while making the failure mode worse (a huge amount of buffered, now-lost work) than if the producer had simply been slowed down earlier.

**Is backpressure only relevant to streaming/real-time systems?**
> No — it applies anywhere a fast producer meets a slower consumer, including batch pipelines (an ETL job reading from a fast source and writing to a slower destination) and simple in-process producer/consumer code, not just live event streams.

**How does backpressure relate to autoscaling?**
> They're complementary at different timescales — backpressure handles the immediate, second-to-second mismatch safely (without data loss or crashes) while autoscaling reacts over a longer window by adding consumer capacity. A system without backpressure can crash long before autoscaling has time to react.

## Related

- [Queues](../messaging/queues.md)
- [Rate Limiting](../../backend/architecture/rate-limiting.md)
- [Dead-Letter Queue](../messaging/dead-letter-queue.md)
- [RabbitMQ](../messaging/rabbitmq.md)
- [Kafka](../messaging/kafka.md)
