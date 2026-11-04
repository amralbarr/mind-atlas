# WebSockets

WebSocket is a communication protocol that upgrades a single [HTTP](http.md) connection into a persistent, full-duplex channel — after the initial handshake, either side (client or server) can send messages to the other at any time, without the request/response cycle [HTTP](http.md) normally requires.

## The Handshake: Upgrading From HTTP

A WebSocket connection starts life as a normal [HTTP](http.md) request carrying special headers asking to switch protocols:

```http
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

Once the server responds `101 Switching Protocols`, the underlying [TCP](tcp.md) connection stops speaking [HTTP](http.md) entirely and becomes a raw WebSocket connection — both sides can now send framed messages independently, in either direction, over the same connection, for as long as it stays open.

## Why Not Just Use HTTP?

Plain [HTTP](http.md) is fundamentally request/response: the client always initiates, and the server can only reply to a request that was already made. That model can't express "the server wants to push a message the instant something happens" without the client resorting to constantly re-asking (polling). WebSockets remove that constraint — the server can push at any moment, and the client can send follow-up messages on the same connection without opening a new one each time.

## Core Characteristics

| Property | Detail |
|---|---|
| **Full-duplex** | Both sides can send at any time, independently — not strictly request-then-response |
| **Persistent** | One [TCP](tcp.md) connection stays open for the life of the session, instead of a new connection (or request) per message |
| **Low overhead per message** | No repeated [HTTP](http.md) headers on every message once the connection is established — just a small frame header |
| **Stateful** | The server must track each open connection, unlike stateless [HTTP](http.md) requests — a real scaling consideration (see below) |
| **Scheme** | `ws://` (plaintext) or `wss://` (over [TLS](tls.md), the WebSocket analogue of [HTTPS](https.md)) |

## A Minimal Example (Node.js)

```javascript
// Server (ws library)
const { WebSocketServer } = require('ws');
const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', (socket) => {
  socket.on('message', (data) => {
    console.log('received:', data.toString());
    socket.send('echo: ' + data);
  });
  socket.send('welcome');
});
```

```javascript
// Browser client
const socket = new WebSocket('wss://example.com/chat');
socket.onopen = () => socket.send('hello');
socket.onmessage = (event) => console.log('got:', event.data);
socket.onclose = () => console.log('connection closed');
```

## The Real Cost: Connection State at Scale

Every open WebSocket ties up a connection (and typically a slot of server memory/file descriptors) for as long as it's open, even while idle — very different from stateless [HTTP](http.md), where a server handles a burst of requests and then holds nothing. This has real architectural consequences:

- **[Horizontal scaling](../backend/architecture/horizontal-scaling.md) is harder** — a message meant for a specific connected user has to reach whichever server instance is holding *that* user's socket, which usually requires a shared [pub/sub](../distributed-systems/messaging/publish-subscribe.md) layer (e.g. Redis) between instances so any instance can "publish" a message that gets routed to the instance actually holding the target connection.
- **Load balancers need sticky sessions or connection-aware routing** — an L4/L7 [load balancer](load-balancing.md) must route a client's reconnect attempts consistently or accept the added complexity of a shared-state backplane.
- **Reconnection is the client's job** — WebSockets don't auto-reconnect like the browser's `EventSource` (used for [SSE](../protocols/sse.md)) does; production clients implement their own reconnect-with-backoff logic.

## WebSockets vs. HTTP Polling vs. SSE

| | WebSockets | Long/Short Polling | [SSE](../protocols/sse.md) |
|---|---|---|---|
| Direction | Bidirectional | Client-initiated, repeated | Server → client only |
| Connection model | One persistent connection | Repeated [HTTP](http.md) requests | One persistent HTTP connection |
| Protocol | Separate (`ws://`/`wss://`, requires upgrade) | Plain HTTP | Plain HTTP (`text/event-stream`) |
| Proxy/firewall friendliness | Can be blocked by strict proxies that don't support the upgrade | Always works — it's just HTTP | Always works — it's just HTTP |
| Best for | Chat, multiplayer games, collaborative editing — anything needing client→server pushes mid-stream | Legacy fallback | One-way streaming ([LLM](../ai/generation/llm.md) token streaming, notifications, live feeds) |

Use plain request/response for ordinary API calls, [SSE](../protocols/sse.md) when only the server needs to push updates, and WebSockets specifically when the client also needs to send data back over the *same* live connection (not just make a new HTTP call).

## Common Questions

**Do WebSockets run over [TCP](tcp.md) or UDP?**
> [TCP](tcp.md). The handshake itself is HTTP (over [TCP](tcp.md)), and the connection remains [TCP](tcp.md)-based afterward — WebSockets don't change the transport layer, only how the two sides use the already-open connection above it.

**Can a WebSocket connection be load balanced normally?**
> Not with the exact same assumptions as stateless HTTP. Since the connection is long-lived and stateful, a load balancer typically needs sticky sessions (routing a client consistently to the same backend instance) or the backend fleet needs a shared mechanism to route messages to whichever instance actually holds a given user's socket.

**Why do WebSocket URLs use `ws://`/`wss://` instead of `http://`/`https://`?**
> To make the protocol switch explicit at the URL level, even though the handshake itself travels over ordinary HTTP under the hood — `wss://` specifically signals "this connection is upgraded to WebSocket and encrypted with [TLS](tls.md)," the WebSocket equivalent of `https://`.

## Related

- [Server-Sent Events (SSE)](../protocols/sse.md)
- [RTSP](../protocols/rtsp.md) — a different streaming protocol, used for pulling live video (e.g. from an IP camera) rather than general bidirectional messaging
- [HTTP](http.md)
- [HTTPS](https.md)
- [TCP](tcp.md)
- [Load Balancing](load-balancing.md)
- [GraphQL](../backend/api/graphql.md) (subscriptions commonly run over WebSockets)
