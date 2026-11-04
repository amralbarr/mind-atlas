# Distributed Systems Overview

A distributed system is multiple computers or services working together as one system over a network.

Instead of:

```text
Client → One Server → Database
```

you have:

```text
Client → API Gateway → Auth Service
                      → Orders Service
                      → Payments Service
                      → Notifications Service
```

Multiple independent systems communicate to form what looks, from the outside, like a single system.

## A Simple Analogy

Think of a restaurant. A single-person restaurant — one person takes orders, cooks, serves, and handles payment — is like a monolithic system. A distributed restaurant has a cashier, a chef, a delivery person, and a manager, each doing a specialized task; together they form one system. Distributed systems appear to users as ONE system even though internally many servers, services, and databases are cooperating.

## Distributed Systems Are Everywhere

Most modern systems are distributed: Google Search, Netflix, YouTube, Amazon, [Kubernetes](../kubernetes/ingress.md) clusters, cloud platforms, and microservices architectures in general.

## Core Characteristics

1. **Multiple nodes** — a node is any computer, server, or service participating in the system.
2. **[Network communication](network-communication.md)** — nodes talk to each other over [HTTP](../../networking/http.md), [gRPC](../../backend/api/grpc.md), [WebSockets](../../networking/websockets.md), [Kafka](../messaging/kafka.md), [RabbitMQ](../messaging/rabbitmq.md), and similar protocols. See [Network Communication](network-communication.md) for a full comparison.
3. **Shared goal** — all nodes work together toward a unified outcome.
4. **Independent failure** — any one node may fail while the others continue operating.

## Why Distributed Systems Exist

- **Scalability** — instead of upgrading one machine, add more machines.
- **High availability** — if one server crashes, others continue serving traffic.
- **Performance** — workload is distributed across many machines.
- **Geographic distribution** — servers placed closer to users (US, Europe, Asia) reduce latency.

## Types of Distributed Systems

- **Client-server** — the basic distributed model: `Client ↔ Server`.
- **Microservices** — many independent backend services. See [Monolith vs Microservices](../../backend/architecture/monolith-vs-microservices.md) for how this compares to a single deployable unit.
- **[Distributed databases](../../databases/distributed/distributed-databases.md)** — e.g. [Cassandra](../../databases/nosql/cassandra.md), [MongoDB](../../databases/nosql/mongodb.md) clusters. See [Distributed Databases](../../databases/distributed/distributed-databases.md).
- **Peer-to-peer** — e.g. BitTorrent, blockchain networks, and mesh topologies. See [Mesh Architecture](mesh-architecture.md).

## Challenges

1. **Network failure** — the network is unreliable; requests may time out, fail, or duplicate.
2. **Latency** — [network communication](network-communication.md) is inherently slower than in-process calls.
3. **Data consistency** — keeping all nodes synchronized is difficult.
4. **Partial failure** — one service may fail while others succeed, creating subtle bugs. For example, if a payment service succeeds but the inventory service fails, the system becomes inconsistent.
5. **Concurrency** — many nodes may update the same data at the same time.

## CAP Theorem

A distributed system can only fully guarantee two of the following three at once:

- Consistency
- Availability
- Partition tolerance

## Eventual Consistency

A common distributed-systems concept: data becomes consistent over time rather than instantly.

## Communication Styles

- **Synchronous** — the caller waits for a response (e.g. [REST](../../backend/api/rest.md), [gRPC](../../backend/api/grpc.md)).
- **Asynchronous** — the caller sends a message and continues (e.g. [Kafka](../messaging/kafka.md), [RabbitMQ](../messaging/rabbitmq.md)).

See [Network Communication](network-communication.md) for the full rundown of each technology.

## Distributed Transactions

A genuinely difficult topic. A traditional database transaction is "all succeed or all rollback" — hard to guarantee across multiple independent services. Common solutions:

- [Saga pattern](saga-pattern.md)
- Outbox pattern
- Event sourcing

## Observability

Distributed systems require centralized logging, tracing, and monitoring — without them, debugging across many nodes is effectively impossible.

| Purpose | Tools |
|---|---|
| Messaging | [Kafka](../messaging/kafka.md), [RabbitMQ](../messaging/rabbitmq.md) |
| Containers | [Docker](../../containers/docker.md) |
| Orchestration | [Kubernetes](../kubernetes/ingress.md) |
| Monitoring | [Prometheus](../../backend/observability/prometheus.md) |
| Tracing | [Jaeger](../../backend/observability/jaeger.md) |
| Logging | [ELK Stack](../../backend/observability/elk-stack.md) |

## Common Misconception

"Distributed system" does not mean "microservices" specifically. [Distributed databases](../../databases/distributed/distributed-databases.md), [Kubernetes](../kubernetes/ingress.md) clusters, and CDNs are all distributed systems too, independent of whether the application itself is a monolith or a set of microservices.

## Common Questions

**What is a distributed system?**

> A distributed system is a collection of independent computers or services that communicate over a network and work together as a unified system.

**Why are distributed systems difficult?** Network failures, latency, consistency, partial failures, and concurrency all compound.

**What are the benefits?** Scalability, availability, fault tolerance, performance.

**What is partial failure?** When one component fails but others continue running.

**What is [eventual consistency](eventual-consistency.md)?** Data may not be instantly synchronized but will become consistent over time.

**Senior-level summary:**

> A distributed system consists of multiple independent nodes communicating over a network to coordinate and provide a unified service. It enables scalability, fault tolerance, and high availability while introducing challenges such as consistency, latency, and distributed coordination.

## Key Takeaway

```text
Distributed system = many computers acting as one system
```

## Related

- [Network Communication](network-communication.md)
- [Distributed Databases](../../databases/distributed/distributed-databases.md)
- [Monolith vs Microservices](../../backend/architecture/monolith-vs-microservices.md)
- [System Design](../../backend/architecture/system-design.md)
- [Mesh Architecture](mesh-architecture.md)
- [Eventual Consistency](eventual-consistency.md)
- [Consensus Algorithms (Raft & Paxos)](consensus-algorithms.md)
- [Backpressure](backpressure.md)
