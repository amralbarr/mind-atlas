# Saga Pattern

The **Saga pattern** is a design pattern used in distributed systems and microservices to manage transactions that span multiple services, without relying on a single global transaction like a traditional database transaction.

## Core Idea

Instead of one large transaction, a saga splits the work into a series of smaller local transactions. Each service:

1. Performs its own local transaction.
2. Publishes an event (or calls the next step).
3. If something fails, triggers a **compensating action** to undo previous steps.

## Why Not Use Normal Transactions?

Classic transactions rely on [ACID](../../databases/relational/acid.md) guarantees, but in distributed systems:

- Each service has its own separate database.
- There is no shared transaction manager.
- Two-phase commit (2PC) is slow and unreliable at scale.

Sagas replace strict atomicity with **[eventual consistency](eventual-consistency.md)** — see [Distributed Transactions](../../databases/distributed/distributed-transactions.md) for how this compares to a traditional multi-database transaction.

## Example: E-Commerce Order

1. Order Service → create order
2. Payment Service → charge user
3. Inventory Service → reserve items

If payment fails: cancel the order.

If inventory fails: refund the payment, then cancel the order.

These undo steps are called **compensating transactions**.

## Two Types of Saga

### Choreography (Event-Based)

Services communicate via events (e.g., through [Kafka](../messaging/kafka.md) or [RabbitMQ](../messaging/rabbitmq.md)) with no central controller:

- `OrderCreated` → Payment Service listens
- `PaymentCompleted` → Inventory Service listens

**Pros:** fully decoupled, no single point of control.
**Cons:** hard to trace the overall flow — logic is spread across many services.

### Orchestration (Central Controller)

One service — the saga orchestrator — drives the flow directly:

```text
Orchestrator → calls Payment → calls Inventory → ...
```

**Pros:** easier to reason about and manage.
**Cons:** the orchestrator becomes a central dependency and a potential bottleneck.

## Flow Visualization

```text
[Start Order]
     ↓
[Create Order]
     ↓
[Charge Payment]
     ↓
[Reserve Inventory]
     ↓
[Success]

If failure at any step:
     ↓
[Compensate Previous Steps]
```

## Key Concepts

- **Local transactions** — each service handles only its own database.
- **Events / messages** — how services communicate, typically over a [queue](../messaging/queues.md) or [message broker](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md).
- **Compensation** — undo logic instead of a database rollback.
- **[Eventual consistency](eventual-consistency.md)** — the system becomes consistent over time rather than instantly.

## When to Use It

Use the saga pattern when:

- The system is built from microservices.
- Each service owns its own database.
- Multi-step workflows need to be reliable without a distributed transaction.

Typical fits include order processing, multi-step workflows, payment plus resource allocation, or any job pipeline that spans several independently deployed services — often paired with an outbox pattern for reliable event publishing.

## Related

- [Decoupling Pipeline Stages](decouple-stages.md)
- [Fan-Out Architecture](fan-out-architecture.md)
- [Queues](../messaging/queues.md)
- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [Distributed Transactions](../../databases/distributed/distributed-transactions.md)
- [ACID](../../databases/relational/acid.md)
