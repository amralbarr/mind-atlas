# Distributed Transactions

A **distributed transaction** is a transaction that spans multiple services or databases and still guarantees that all parts succeed or all fail together.

> A distributed transaction ensures that operations across multiple independent systems behave like a single atomic transaction.

## Example

Imagine this flow in an AI pipeline:

```text
1. Save PipelineRun in DB
2. Send job to queue
3. Store embedding in vector DB
4. Save results in main DB
```

If step 1 and step 2 succeed but step 3 fails, the system is left in an inconsistent state — without a distributed transaction, there's no built-in way to undo the earlier steps.

## Why This Is a Problem

In distributed systems — multiple databases, multiple services, [message queues](../../distributed-systems/messaging/queues.md) — you cannot rely on a single database's:

```text
BEGIN TRANSACTION ... COMMIT
```

because the operations span systems that don't share a transaction log.

### Real-World Analogy

Booking a trip requires a flight seat, a hotel room, and a car rental. If the hotel booking fails after the flight is already booked, you don't want a partial booking — that's the same class of problem as a distributed transaction.

## How Distributed Transactions Are Handled

There are three main strategies.

### 1. Two-Phase Commit (2PC)

Used in strict systems.

**Phase 1 — Prepare:** all services report "I can commit."

**Phase 2 — Commit:** if all agree, everything is committed together.

Problems with 2PC:

- Slow
- Blocking (participants hold locks while waiting)
- Not scalable for modern microservices

### 2. Saga Pattern (Most Used)

Instead of strict atomicity, a Saga breaks a transaction into steps plus **compensating actions**.

Example:

```text
Step 1: Save PipelineRun
Step 2: Send queue message
Step 3: Store embedding
```

If step 3 fails, compensation runs:

```text
→ delete PipelineRun
→ cancel job
```

Why the [Saga pattern](../../distributed-systems/patterns/saga-pattern.md) is popular:

- Scalable
- Asynchronous
- Works well with microservices
- Fits AI/data pipelines naturally

### 3. Eventual Consistency

Instead of enforcing immediate consistency, the system becomes correct over time. Example: an embedding is stored later, and retry workers fix any missing data.

A system built from a database plus a queue with sequential execution is already using a Saga-style design, even without full distributed-transaction machinery — though it typically stops short of formal compensation logic.

## Key Challenges

Distributed transactions must handle:

- Partial failures
- Retries
- Duplicate messages
- Inconsistent intermediate state

They are hard because networks can fail, services can crash, messages can be duplicated, and timing is unpredictable — so strict atomicity is avoided in favor of the patterns above.

## Applying This to an AI Pipeline

Consider a pipeline like:

```text
OCR → Chunking → Embedding → RAG → LLM → Output
```

Distributed transaction concerns include: what if embedding fails? What if the [LLM](../../ai/generation/llm.md) call crashes? What if a queue message is delivered twice? These are addressed with the [Saga pattern](../../distributed-systems/patterns/saga-pattern.md), retries, and [idempotency](../../backend/api/idempotency.md).

## The Outbox Pattern (Related Pattern)

The **Outbox Pattern** solves a closely related problem: reliably sending events from a database to other services (for example, via [Kafka](../../distributed-systems/messaging/kafka.md)) without losing or duplicating them.

### The Dual-Write Problem

See [The Dual-Write Problem](dual-write-problem.md) for the general pattern (database + cache, database + search index, migration cutovers) this section works out for the database + message broker case specifically.

Doing this directly is unsafe:

```text
1. Save data to DB
2. Publish event to Kafka
```

If the DB commit succeeds but the [Kafka](../../distributed-systems/messaging/kafka.md) publish fails, the system becomes inconsistent — this is the same "step 1 succeeds, step 2 fails" problem described above.

### The Safe Version

```text
1. Save data to DB
2. Save event in an OUTBOX table (same transaction as step 1)
3. A separate process reads the outbox and sends events to Kafka
```

Example outbox table:

```sql
outbox_events
------------------------
id
aggregate_id
event_type
payload
status (pending/sent)
created_at
```

### Architecture Flow

```text
[Application DB]
      |
      | (single transaction)
      v
[Business Table + Outbox Table]
      |
      v
[Outbox Relay Worker]
      |
      v
Kafka Topic
      |
      v
Microservices (Consumers)
```

1. The application writes the business row and an outbox row (e.g. `pipeline_started`) in one DB transaction.
2. A relay worker polls the outbox table, or uses Change Data Capture (CDC), to find unsent events.
3. The worker publishes the event to a [Kafka](../../distributed-systems/messaging/kafka.md) topic.
4. [Kafka](../../distributed-systems/messaging/kafka.md) distributes the event to downstream consumers ([OCR](../../ai/ingestion/ocr.md) service, logging, analytics, etc.).

### Implementation Styles

**Polling-based outbox** — a worker runs `SELECT * FROM outbox WHERE status = 'pending'`. Simple, but slower.

**CDC-based outbox** — tools like Debezium or [Kafka](../../distributed-systems/messaging/kafka.md) Connect read the database's write-ahead log and stream changes directly to [Kafka](../../distributed-systems/messaging/kafka.md). Real-time and scalable, but more complex to operate.

### What Each Piece Solves

| Problem                     | Solution                       |
| ---------------------------- | -------------------------------- |
| DB saved but [Kafka](../../distributed-systems/messaging/kafka.md) publish failed | Outbox stores the event safely     |
| Duplicate events                  | Outbox + id tracking                  |
| Lost messages                       | No direct publish from the app          |
| Consistency issues                    | Single DB transaction covers both writes  |

> Outbox pattern guarantees reliable event creation. [Kafka](../../distributed-systems/messaging/kafka.md) handles event distribution and streaming. Together they solve [the dual-write problem](dual-write-problem.md) between a database and a message broker: outbox is the safety layer, [Kafka](../../distributed-systems/messaging/kafka.md) is the delivery layer.

## Common Questions

**Q1. What is a distributed transaction?**

> A distributed transaction is a mechanism to ensure consistency across multiple services or databases in a distributed system, where operations must either all succeed or be compensated if any step fails.

**Q2. What's the difference between 2PC and the [Saga pattern](../../distributed-systems/patterns/saga-pattern.md)?**

2PC enforces synchronous, blocking atomicity across all participants at commit time. The [Saga pattern](../../distributed-systems/patterns/saga-pattern.md) instead runs each step independently and reacts to failure with compensating actions, trading strict atomicity for scalability and asynchrony.

**Senior-level answer:**

> A distributed transaction coordinates state changes across multiple independent systems so they behave as one atomic unit despite network partitions, partial failures, and concurrent access — typically implemented via two-phase commit for strict consistency or the [Saga pattern](../../distributed-systems/patterns/saga-pattern.md) with compensating actions for scalable, eventually-consistent workflows.

**One-line mental model:**

> Make multiple services behave like one transaction, even though they are not connected.

## Related

- [ACID](../relational/acid.md)
- [SQL](../relational/sql.md)
- [Database Indexing](../relational/indexing.md)
- [Distributed Databases](distributed-databases.md)
- [Distributed Systems Overview](../../distributed-systems/patterns/distributed-systems-overview.md)
- [Optimistic Locking](../relational/optimistic-locking.md) — a lighter-weight, single-database alternative to coordinating locks when the conflict-detection problem doesn't actually span multiple systems
- [Pessimistic Locking](../relational/pessimistic-locking.md) — the single-database equivalent of blocking-before-proceeding; coordinating this guarantee across multiple databases is exactly what makes distributed transactions hard
