# TCP

**TCP (Transmission Control Protocol)** is one of the core communication protocols of the Internet — a reliable, connection-oriented protocol for sending data between computers.

It underlies most familiar internet protocols and tools: [HTTP](http.md), [HTTPS](https.md), [WebSockets](websockets.md), databases, general APIs, [SSH](../protocols/ssh.md), and email protocols.

## Simple Definition

> TCP is a reliable, connection-oriented protocol for sending data between computers.

TCP guarantees:

- Ordered delivery
- Reliable delivery
- Error checking

For example, if a sender transmits `A B C`, TCP guarantees the receiver gets `A B C` — in that exact order — even if the underlying network reorders or loses packets along the way.

## Characteristics

| Feature          | TCP |
| ---------------- | --- |
| Reliable         | Yes |
| Ordered          | Yes |
| Connection-based | Yes |
| Error checking   | Yes |
| Fastest possible | No  |

## Connection Setup: The Three-Way Handshake

Before any data is sent, TCP establishes a connection via a handshake:

```text
Client → SYN
Server → SYN-ACK
Client → ACK
```

Once this completes, the connection is established and data can flow.

## Why TCP Is Reliable

TCP achieves reliability through:

- **Acknowledgments** — the receiver confirms what it has received.
- **Retransmission** — if a packet is lost, TCP resends it.
- **Sequencing** — packets are numbered and reassembled in order.
- **Flow control** — the sender is prevented from overwhelming the receiver.

## Where TCP Sits in the Stack

```text
Application Layer
Transport Layer  ← TCP here
Internet Layer
Network Layer
```

TCP is a Layer 4 (transport layer) protocol.

## TCP vs. UDP

UDP (User Datagram Protocol) is the other major transport protocol, and the comparison is one of the most common topics in networking.

UDP's philosophy is "send and forget" — there's no guarantee of delivery. Packets may arrive out of order, duplicated, or not at all. In exchange, UDP is significantly faster, because it skips connection setup, acknowledgments, and retransmission — trading reliability for speed.

| Feature         | TCP        | UDP       |
| --------------- | ---------- | --------- |
| Reliable        | Yes        | No        |
| Ordered         | Yes        | No        |
| Speed           | Slower     | Faster    |
| Connection      | Stateful   | Stateless |
| Retransmission  | Yes        | No        |
| Streaming/video | Less ideal | Excellent |
| APIs/web        | Common     | Rare      |

**Common analogy:**

- TCP is like registered mail with confirmation of delivery.
- UDP is like throwing papers into the air quickly — most arrive, but there's no guarantee.

### When Each Is Used

**TCP** — downloading a file: all data must arrive correctly; missing bytes are unacceptable. Also used by [HTTP](http.md)/[HTTPS](https.md), APIs, databases (e.g. [PostgreSQL](../databases/relational/postgresql.md), Redis), [SSH](../protocols/ssh.md), and message brokers like [Kafka](../distributed-systems/messaging/kafka.md) and [RabbitMQ](../distributed-systems/messaging/rabbitmq.md), all of which depend on TCP's reliability.

**UDP** — a live video call: speed matters more than perfection, and small packet loss is acceptable. Also used for live video streaming, online gaming, VoIP, [DNS](dns.md) queries, and real-time telemetry.

```text
HTTP
  ↓
TCP
  ↓
IP
```

[WebSockets](websockets.md) also run over TCP, since they need ordered, reliable, real-time communication.

## TCP's Drawbacks

1. **Head-of-line blocking** — one lost packet blocks delivery of everything behind it, even if later packets already arrived.
2. **Handshake overhead** — connection setup costs a round trip before any data is sent.
3. **Higher latency** — compared to UDP, due to the above.

## QUIC and HTTP/3

QUIC is a modern transport protocol developed by Google. It runs on top of UDP but adds the reliability, multiplexing, and security that raw UDP lacks — aiming to keep UDP's speed while avoiding TCP's head-of-line blocking and handshake overhead.

[HTTP](http.md)/3 is built on QUIC, and represents the most significant recent evolution of the web transport layer — improving connection speed, performance, and mobile network switching compared to TCP-based [HTTP](http.md)/1.1 and [HTTP](http.md)/2.

## Common Questions

**What is TCP?**

> TCP is a reliable, connection-oriented transport protocol that guarantees ordered and error-checked data delivery between systems.

**Difference between TCP and UDP?**

| TCP              | UDP            |
| ---------------- | -------------- |
| Reliable         | Fast           |
| Ordered          | Unordered      |
| Connection-based | Connectionless |

**Why does [HTTP](http.md) use TCP?** Because web requests require reliable, ordered delivery.

**Why do games often use UDP?** Because low latency matters more than perfect reliability.

**What is the handshake?** The connection-establishment process that happens before data transfer begins.

**Senior-level summary:**

> TCP is a connection-oriented transport protocol that provides reliable, ordered, and error-checked communication between distributed systems. It underpins most modern web and backend protocols, while alternatives like UDP prioritize lower latency over delivery guarantees.

## Key Takeaway

```text
TCP = reliable delivery
UDP = fast delivery
```

## Related

- [DNS](dns.md)
- [HTTP](http.md)
- [Network Communication](../distributed-systems/patterns/network-communication.md)
