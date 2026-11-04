# Network Communication

A comparison of [HTTP](../../networking/http.md)/[REST](../../backend/api/rest.md), [JSON](../../programming/fundamentals/json.md)-RPC, [gRPC](../../backend/api/grpc.md), [WebSockets](../../networking/websockets.md), [Kafka](../messaging/kafka.md), and [RabbitMQ](../messaging/rabbitmq.md) — six common backend and system-design topics that solve *different* communication problems in distributed systems.

## Quick Comparison

| Technology                                                           | Type                  | Communication Style      | Best For                                |
| -------------------------------------------------------------------- | --------------------- | ------------------------ | --------------------------------------- |
| [HTTP](../../networking/http.md) / [REST](../../backend/api/rest.md) | Request/response      | Synchronous              | General-purpose APIs                    |
| [JSON](../../programming/fundamentals/json.md)-RPC                   | RPC                   | Synchronous              | Simple, transport-agnostic remote calls |
| [gRPC](../../backend/api/grpc.md)                                    | RPC                   | Synchronous              | High-performance service-to-service     |
| [WebSockets](../../networking/websockets.md)                         | Persistent connection | Real-time, bidirectional | Live updates / chat                     |
| [Kafka](../messaging/kafka.md)                                       | Event streaming       | Asynchronous             | Massive-scale event systems             |
| [RabbitMQ](../messaging/rabbitmq.md)                                 | Message queue         | Asynchronous             | Reliable task/message processing        |
|                                                                      |                       |                          |                                         |

## HTTP / REST

The most common API communication style: a client sends a request, a server sends a response.

```text
Client → Request
Server → Response
```

```http
GET /users/1
```

```json
{ "id": 1, "name": "Amr" }
```

**Characteristics:** stateless, text-based ([JSON](../../programming/fundamentals/json.md)), easy to debug, universally supported.

**Pros:** simple, human-readable, browser-native, easy to integrate.

**Cons:** more bandwidth, slower than binary protocols, per-request connection overhead.

**Best for:** frontend-to-backend traffic, public APIs, CRUD APIs. In [NestJS](https://nestjs.com/), `@Controller('users')` typically exposes an [HTTP](../../networking/http.md) API.

## JSON-RPC

[JSON](../../programming/fundamentals/json.md)-RPC is a minimal **remote procedure call** protocol: instead of [REST](../../backend/api/rest.md)'s "resources and verbs" model (`GET /users/1`), the client just names a method and passes arguments, over any transport (commonly plain [HTTP](../../networking/http.md), but equally at home over a raw [TCP](../../networking/tcp.md) socket or a WebSocket connection):

```json
// Request
{ "jsonrpc": "2.0", "method": "getUser", "params": { "id": 1 }, "id": 42 }

// Response
{ "jsonrpc": "2.0", "result": { "id": 1, "name": "Amr" }, "id": 42 }
```

The `id` field pairs each response back to its request — necessary because, unlike a plain [HTTP](../../networking/http.md) request/response pair, [JSON](../../programming/fundamentals/json.md)-RPC calls can be sent in a batch or over a connection carrying multiple concurrent in-flight calls. A request sent with no `id` (or an explicit `"notification"` shape in some implementations) tells the server not to bother replying at all — a fire-and-forget call.

**Characteristics:** plain [JSON](../../programming/fundamentals/json.md) (human-readable, easy to debug), no built-in resource/URL model — everything is a named method call, transport-agnostic (doesn't assume [HTTP](../../networking/http.md)'s verbs/status codes carry any meaning).

**Pros:** very simple to implement and consume, works unchanged over [HTTP](../../networking/http.md) or a raw socket, natural fit for RPC-style APIs that don't map cleanly onto [REST](../../backend/api/rest.md)'s CRUD-on-resources model.

**Cons:** no built-in tooling ecosystem as rich as [REST](../../backend/api/rest.md)'s (caching via [HTTP](../../networking/http.md) semantics, standard status-code-based error handling) since it deliberately doesn't lean on the transport's own semantics; every error has to be modeled explicitly in the [JSON](../../programming/fundamentals/json.md) payload rather than reused from [HTTP status codes](../../backend/api/http-status-codes.md).

**Best for:** blockchain/wallet APIs (a very common real-world use), internal tooling with simple method-call semantics, editor/IDE protocols (the Language Server Protocol is built on [JSON](../../programming/fundamentals/json.md)-RPC) — anywhere a simple, transport-agnostic call/response shape is a better fit than modeling everything as [REST](../../backend/api/rest.md) resources.

### JSON-RPC vs. gRPC

|                  | [JSON](../../programming/fundamentals/json.md)-RPC            | [gRPC](../../backend/api/grpc.md)                      |
| ---------------- | ------------------------------------------------------------- | ------------------------------------------------------ |
| Wire format      | Plain [JSON](../../programming/fundamentals/json.md) (text)                                             | Binary protobuf                                        |
| Transport        | Any ([HTTP](../../networking/http.md), raw socket, WebSocket) | [HTTP](../../networking/http.md)/2 specifically        |
| Typing           | None built-in (a hand-written contract, if any)               | Strong, contract-first (`.proto` schema)               |
| Setup complexity | Minimal                                                       | Higher (codegen, protobuf tooling)                     |
| Best for         | Simple, low-volume RPC needs                                  | High-performance, high-volume service-to-service calls |

## gRPC

See [gRPC](../../backend/api/grpc.md) for the full atomic treatment (call types, contract-first `.proto` workflow, [gRPC](../../backend/api/grpc.md)-Web). Summary below for how it fits alongside the other options on this page.

[gRPC](../../backend/api/grpc.md) (Google Remote Procedure Call) is a high-performance communication protocol for service-to-service calls — conceptually like calling a local function remotely:

```text
Service A ↔ Service B
```

It runs over [HTTP](../../networking/http.md)/2 and uses Protocol Buffers (protobuf) as a binary wire format, which is smaller and faster than [JSON](../../programming/fundamentals/json.md):

```proto
service UserService {
  rpc GetUser(UserRequest) returns (UserResponse);
}
```

**Characteristics:** binary, strongly typed, contract-first, very fast.

**Pros:** high performance, low latency, strong typing, native streaming support.

**Cons:** harder to debug, less browser-friendly, more complex setup.

**Best for:** microservices, internal backend communication, AI inference services, high-throughput systems.

### HTTP vs gRPC

| Feature | [HTTP](../../networking/http.md) [REST](../../backend/api/rest.md) | [gRPC](../../backend/api/grpc.md) |
|---|---|---|
| Format | [JSON](../../programming/fundamentals/json.md) | Binary protobuf |
| Speed | Slower | Faster |
| Human readable | Yes | No |
| Browser friendly | Yes | Limited |
| Typing | Weak | Strong |

## WebSockets

See [WebSockets](../../networking/websockets.md) for the full atomic treatment (handshake, connection-state scaling trade-offs, comparison with [SSE](../../protocols/sse.md)/polling). Summary below for how it fits alongside the other options on this page.

A persistent, full-duplex connection. Unlike [HTTP](../../networking/http.md)'s request → response → close cycle, a WebSocket connection stays open, and the server can push data at any time.

```text
Client ⇄ Server  (real-time, persistent connection)
```

**Characteristics:** built on a persistent [TCP](../../networking/tcp.md) connection, bidirectional, low latency.

**Pros:** real-time updates, very low latency, efficient for frequent updates.

**Cons:** harder to scale, stateful connections, more infrastructure complexity.

**Best for:** chat apps, live dashboards, multiplayer games, stock prices, IoT live telemetry. In [Socket.IO](https://socket.io/), `@WebSocketGateway()` is a typical entry point.

### HTTP vs WebSockets

| [HTTP](../../networking/http.md) | WebSocket |
|---|---|
| Stateless | Stateful |
| Request/response | Real-time |
| Short-lived | Persistent |
| Client initiates | Either side initiates |

## Kafka

[Kafka](../messaging/kafka.md) is a distributed **event streaming platform** — not a simple queue, and that distinction matters. Producers publish events; consumers process them asynchronously:

```text
Producer → Kafka → Consumers
```

Example: an `OrderCreated` event might be consumed independently by analytics, notifications, and billing services.

**Characteristics:** distributed, partitioned, durable, replayable, extremely scalable. Consumers track *offsets* — a record of where they last stopped reading — which is what makes replay and reprocessing possible. This is the key thing that separates [Kafka](../messaging/kafka.md) from a traditional queue: messages can be replayed and reprocessed rather than consumed once and discarded.

**Pros:** massive scalability, event replay, distributed durability, stream processing.

**Cons:** operational complexity, learning curve, overkill for small systems.

**Best for:** event-driven systems, analytics pipelines, telemetry, log aggregation, streaming architectures.

## RabbitMQ

[RabbitMQ](../messaging/rabbitmq.md) is a message broker / queue system focused on reliable task delivery:

```text
Producer → Queue → Consumer
```

Example: dispatching email-sending jobs.

**Characteristics:** queue-based, acknowledgments, routing, retries.

**Pros:** reliable delivery, well-suited to task queues, built-in retries, simpler operationally than [Kafka](../messaging/kafka.md).

**Cons:** less scalable than [Kafka](../messaging/kafka.md), lower throughput.

**Best for:** background jobs, email queues, payment processing, task distribution.

### Kafka vs RabbitMQ

| Feature       | [Kafka](../messaging/kafka.md) | [RabbitMQ](../messaging/rabbitmq.md) |
| ------------- | ------------------------------ | ------------------------------------ |
| Model         | Event streaming                | Message queue                        |
| Replay events | Yes                            | Limited                              |
| Throughput    | Very high                      | Medium                               |
| Ordering      | Partition ordering             | Queue ordering                       |
| Use case      | Streaming/events               | Task processing                      |

## Choosing the Right Technology

Simple mental model:

```text
HTTP        → ask a question, get an answer
JSON-RPC    → simple, transport-agnostic remote method call
gRPC        → fast backend-to-backend function calls
WebSockets  → open live communication channel
RabbitMQ    → task/job queue
Kafka       → massive event streaming pipeline
```

A common real-world architecture combines several of these:

```text
Frontend                          → HTTP API
Realtime updates                  → WebSockets
Microservice internal comms       → gRPC
Background jobs                   → RabbitMQ
Analytics / events                → Kafka
```

### Synchronous vs Asynchronous

| Technology | Style |
|---|---|
| HTTP | Synchronous |
| [JSON](../../programming/fundamentals/json.md)-RPC | Synchronous (or fire-and-forget via notifications) |
| [gRPC](../../backend/api/grpc.md) | Synchronous |
| [WebSockets](../../networking/websockets.md) | Real-time, persistent |
| [Kafka](../messaging/kafka.md) | Asynchronous |
| [RabbitMQ](../messaging/rabbitmq.md) | Asynchronous |

Note this is sync/async at the level of two *services* talking over a network — does the caller wait for the callee's response before continuing, or does it fire a message and move on. That's a distinct, narrower idea from [asynchronous / non-blocking execution](../../programming/fundamentals/asynchronous-non-blocking-execution.md) within a single process's own [I/O](../../programming/fundamentals/io.md) model (whether its own thread blocks while waiting on an operation) — a service can make a synchronous, wait-for-the-response HTTP call while still being implemented with fully non-blocking [I/O](../../programming/fundamentals/io.md) internally.

## Common Questions

**When would you choose [Kafka](../messaging/kafka.md) over [RabbitMQ](../messaging/rabbitmq.md)?**

> [Kafka](../messaging/kafka.md) is preferred for high-throughput event streaming and event-replay architectures, while [RabbitMQ](../messaging/rabbitmq.md) is better suited to reliable task queues and traditional message-processing workflows.

**When would you choose [WebSockets](../../networking/websockets.md)?**

When the server needs to push real-time updates continuously, rather than waiting for the client to poll.

**Why is [gRPC](../../backend/api/grpc.md) faster than [REST](../../backend/api/rest.md)?**

Because it uses HTTP/2 and binary protobuf [serialization](../../programming/fundamentals/serialization.md) instead of JSON text payloads.

**Senior-level summary:**

> HTTP and [gRPC](../../backend/api/grpc.md) are primarily synchronous communication protocols, with [gRPC](../../backend/api/grpc.md) optimized for high-performance service-to-service communication. [WebSockets](../../networking/websockets.md) provide persistent, bidirectional real-time communication, while [RabbitMQ](../messaging/rabbitmq.md) focuses on reliable message queuing and [Kafka](../messaging/kafka.md) specializes in distributed event streaming at massive scale.

## Key Takeaway

```text
HTTP       → APIs
gRPC       → fast services
WebSockets → realtime
RabbitMQ   → tasks
Kafka      → event streams
```

## Related

- [Distributed Systems Overview](distributed-systems-overview.md)
- [Queues](../messaging/queues.md)
- [Fan-Out Architecture](fan-out-architecture.md)
- [Distributed Databases](../../databases/distributed/distributed-databases.md)
- [System Design](../../backend/architecture/system-design.md)
- [HTTP](../../networking/http.md)
- [HTTPS](../../networking/https.md)
- [gRPC](../../backend/api/grpc.md)
- [WebSockets](../../networking/websockets.md)
- [Backpressure](backpressure.md)
- [Asynchronous / Non-Blocking Execution](../../programming/fundamentals/asynchronous-non-blocking-execution.md) — the related-but-distinct single-process [I/O](../../programming/fundamentals/io.md) concept (see "Synchronous vs Asynchronous" above for how it differs)
