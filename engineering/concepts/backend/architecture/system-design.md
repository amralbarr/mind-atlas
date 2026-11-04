# System Design

System design is the practice of structuring how the pieces of a backend — services, data stores, queues, caches, and network boundaries — fit together to meet requirements for scale, reliability, and maintainability. It sits one level above any single technology choice: the same building blocks (queues, caches, load balancers) get assembled differently depending on the problem.

## Core Concepts and Building Blocks

A working system design vocabulary covers:

- [Monolith vs Microservices](monolith-vs-microservices.md) — the fundamental decomposition question
- Event-driven systems
- [Message queues](../../distributed-systems/messaging/queues.md) (see [Queues](../../distributed-systems/messaging/queues.md))
- [Kafka](../../distributed-systems/messaging/kafka.md) and [RabbitMQ](../../distributed-systems/messaging/rabbitmq.md) as concrete queue/streaming technologies
- Redis as a queue/cache
- WebSocket scaling
- [Horizontal scaling](horizontal-scaling.md)
- Load balancers, reverse proxies, and API gateways
- Distributed systems fundamentals (see [Distributed Systems Overview](../../distributed-systems/patterns/distributed-systems-overview.md))
- [Caching strategies](caching-strategies.md)
- CQRS (Command Query Responsibility Segregation)
- The [Saga pattern](../../distributed-systems/patterns/saga-pattern.md) for [distributed transactions](../../databases/distributed/distributed-transactions.md)

These building blocks recur across almost every real architecture decision — the skill is knowing which combination fits a given set of constraints (traffic pattern, consistency requirements, team size, operational budget).

## Common System Design Prompts

These building blocks are typically exercised through open-ended design prompts, such as:

- Design WhatsApp
- Design Uber
- Design YouTube
- Design an IoT telemetry system
- Design a real-time dashboard
- Design an AI agents platform
- How would you scale [WebSockets](../../networking/websockets.md)?
- How do you prevent bottlenecks?
- How does caching work, and where would you place it?

## Worked Example: Choosing a Storage Architecture

To see these tradeoffs applied to a concrete decision, consider a common real-world choice: how should a backend handle file and media storage (uploads, AI/[RAG](../../ai/rag/rag.md) documents, generated media)? Two architectures are typically on the table.

### Option 1: Object Storage + CDN

**Flow:**

```text
User → Cloudflare CDN → Object Storage (S3 / MinIO)
```

**Pros:**

- Highly scalable — handles millions of files easily
- Decoupled from the backend, so the API stays fast
- Built-in redundancy and durability
- Works well with AI pipelines ([RAG](../../ai/rag/rag.md), media, logs)
- Easy to generate signed URLs for direct client access
- [CDN](../../networking/cdn.md) caching in front of [object storage](../../cloud/infrastructure/object-storage.md) is very efficient

**Cons:**

- Slightly more complex setup
- Requires managing a storage service, or paying for S3
- Adds an extra layer between API and storage

### Option 2: Nginx + CDN + Local Disk Uploads

**Flow:**

```text
User → Cloudflare CDN → Nginx → Local Disk (/uploads)
```

**Pros:**

- Very simple setup, no extra services
- Faster to stand up for small projects
- Easy to debug

**Cons:**

- Not scalable
- Risk of disk full / data loss
- Hard to use across multiple servers
- Bad fit for large files or AI datasets
- Backups become a manual headache
- Deployment carries a risk of losing files

### Direct Comparison

| Feature | [Object Storage](../../cloud/infrastructure/object-storage.md) + [CDN](../../networking/cdn.md) | [Nginx](../api-gateways/nginx.md) Local + [CDN](../../networking/cdn.md) |
|---|---|---|
| Scalability | High | Limited |
| Performance | Optimized | Depends on server |
| Reliability | Very high | Risky |
| Multi-server support | Easy | Hard |
| AI / [RAG](../../ai/rag/rag.md) usage | Well-suited | Not ideal |
| Setup complexity | Medium | Simple |
| Cost | Pay for S3, or free with MinIO | Cheap |

### Decision Framework

For AI/media-heavy workloads — [RAG](../../ai/rag/rag.md) pipelines, generated media, TTS output, general file uploads — avoid relying on local disk storage; it doesn't scale past a single server and puts data at risk. Prefer [object storage](../../cloud/infrastructure/object-storage.md) (S3 or self-hosted MinIO) behind a [CDN](../../networking/cdn.md).

**Use [object storage](../../cloud/infrastructure/object-storage.md) when:**

- The workload involves AI, media, or documents
- Growth is expected
- Multiple service instances need shared access to the same files
- Reliability matters

**Use local storage when:**

- It's a small test project or MVP
- The system will run on a single server indefinitely

In short: local storage is fine short-term, but [object storage](../../cloud/infrastructure/object-storage.md) is the production-grade choice once the system needs to scale or run on more than one server.

### Example Recommended Architecture

Putting it together, a typical production setup looks like:

```text
User
  ↓
Cloudflare (CDN + SSL)
  ↓
Nginx (API reverse proxy only)
  ↓
Backend (e.g. NestJS)
  ↓
MinIO (object storage)
```

Here [Nginx](../api-gateways/nginx.md)'s job is reduced to reverse-proxying API traffic — it no longer serves files directly from local disk — while MinIO (or S3) owns file storage and the [CDN](../../networking/cdn.md) owns edge caching and [TLS](../../networking/tls.md) termination.

## Key Takeaway

System design is fundamentally about tradeoffs: every pattern above (queues, caching, [sharding](../../databases/distributed/sharding.md), [object storage](../../cloud/infrastructure/object-storage.md) vs. local disk) trades some combination of simplicity, cost, latency, and operational overhead for scalability and reliability. The worked storage example is a small, concrete instance of the same reasoning that applies to bigger prompts like "design Uber" or "design YouTube."

## Related

- [Monolith vs Microservices](monolith-vs-microservices.md)
- [Queues](../../distributed-systems/messaging/queues.md)
- [Mesh Architecture](../../distributed-systems/patterns/mesh-architecture.md)
- [Fan-Out Architecture](../../distributed-systems/patterns/fan-out-architecture.md)
- [Distributed Systems Overview](../../distributed-systems/patterns/distributed-systems-overview.md)
- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Load Balancing](../../networking/load-balancing.md)
- [Caching Strategies](caching-strategies.md)
- [Rate Limiting](rate-limiting.md)
