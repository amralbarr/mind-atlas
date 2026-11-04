# ZeroMQ (ØMQ)

ZeroMQ is fundamentally different from every other entry in this vault's messaging notes: it's a **messaging library**, not a broker — there's no separate server process to run, deploy, or operate at all. Two processes using ZeroMQ talk to each other over sockets directly; ZeroMQ just makes those sockets behave like message-passing primitives (queuing, reconnection, multiple patterns) instead of raw bytes.

## No Broker, By Design

| | Broker-based ([RabbitMQ](rabbitmq.md), [Kafka](kafka.md), [NATS](nats.md)) | ZeroMQ |
|---|---|---|
| Extra process to run | Yes — the broker itself | No — just a library linked into your application |
| Message durability | Broker can persist messages | None built in — if a socket has nothing to send to, the library's own buffering is the only cushion |
| Routing/fan-out logic | Lives in the broker | Lives in application code, using ZeroMQ's socket patterns |

This trade-off is deliberate: removing the broker removes a hop (and a single point of operational failure) at the cost of taking on more responsibility in application code for anything a broker would otherwise handle (persistence, routing, retry).

## Core Socket Patterns

ZeroMQ's main [abstraction](../../programming/fundamentals/abstraction.md) is a small set of **socket types**, each encoding a different communication pattern:

| Pattern | Sockets | Shape |
|---|---|---|
| **Request-Reply** | `REQ` / `REP` | Strict ping-pong — one request, one reply, in lockstep |
| **[Publish-Subscribe](publish-subscribe.md)** | `PUB` / `SUB` | Fire-and-forget broadcast, subscribers filter by topic prefix |
| **Pipeline** | `PUSH` / `PULL` | Load-balanced fan-out to a pool of workers — a very lightweight distributed-task pattern |

## Example: PUSH/PULL (Task Distribution)

```python
# Producer (PUSH)
import zmq
context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.bind("tcp://*:5557")
socket.send_json({"task": "resize_image", "id": 42})

# Worker (PULL)
socket = context.socket(zmq.PULL)
socket.connect("tcp://localhost:5557")
while True:
    job = socket.recv_json()
    process(job)
```

Multiple workers connecting to the same `PUSH` socket automatically load-balance the incoming work round-robin — no broker coordinating it, the library handles the fan-out.

## Common Questions

**When does ZeroMQ make sense over a real broker?**
> When ultra-low latency matters more than durability/persistence, when adding an extra broker process/dependency is genuinely unacceptable (embedded systems, tightly-coupled internal services), or when the application already needs custom routing logic that a generic broker doesn't offer particularly well anyway.

**What happens to a message if the receiving process isn't running yet?**
> Depends on the socket type and its buffering configuration (the "high water mark") — there's no persistent broker holding messages for an offline consumer the way [Kafka](kafka.md) or [RabbitMQ](rabbitmq.md) would, so ZeroMQ is a poor fit for scenarios where consumers come and go unpredictably and can't afford to miss messages sent while offline.

## Related

- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [ActiveMQ](activemq.md)
- [NATS](nats.md)
