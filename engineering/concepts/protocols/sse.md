# Server-Sent Events (SSE)

Server-Sent Events (SSE) is a web standard, defined as part of the HTML5 spec, for a server to push a one-way stream of text updates to a client over a single long-lived [HTTP](../networking/http.md) connection. Unlike a normal [HTTP](../networking/http.md) response, the connection stays open and the server can keep writing new messages to it over time, which the browser (or any client library) receives incrementally. It's the simplest way to stream a sequence of updates from server to client — no protocol upgrade, no bidirectional handshake, just plain [HTTP](../networking/http.md) with a special content type.

## How It Extends HTTP

SSE is not a separate protocol like [WebSockets](../networking/websockets.md) — it's a convention on top of a normal [HTTP](../networking/http.md) response:

| Regular [HTTP](../networking/http.md) response | SSE response |
|---|---|
| `Content-Type: application/json` (or similar), body sent once, connection closes | `Content-Type: text/event-stream`, connection stays open, body is written incrementally as a series of events |
| Client gets one complete response | Client receives a stream of discrete `data:` events over time |

Because it's plain [HTTP](../networking/http.md), SSE passes through firewalls, proxies, and load balancers that would block or mishandle a WebSocket upgrade, and it works over HTTP/1.1 and HTTP/2 without special server support.

## Wire Format

Each event is a small block of text terminated by a blank line, with named fields:

```
data: {"token": "Hello"}

data: {"token": " world"}

event: done
data: {"finish_reason": "stop"}

```

| Field | Purpose |
|---|---|
| `data:` | The payload for this event (can repeat across multiple lines for one event) |
| `event:` | An optional event name/type, so the client can dispatch different handlers per event type |
| `id:` | An optional event ID, used for resuming a stream after a disconnect |
| `retry:` | An optional reconnection delay (ms) the client should wait before retrying |

A blank line marks the end of one event. Comments (ignored by clients) start with `:`.

## SSE vs WebSockets vs Long Polling

| | SSE | [WebSockets](../networking/websockets.md) | Long Polling |
|---|---|---|---|
| Direction | Server → client only | Bidirectional | Client → server → client (repeated) |
| Protocol | Plain HTTP (`text/event-stream`) | Separate protocol (`ws://`/`wss://`, requires upgrade) | Plain HTTP, repeated requests |
| Firewall/proxy friendly | Yes | Sometimes blocked (upgrade handshake) | Yes |
| Auto-reconnect | Built into the browser `EventSource` API | Manual | Manual (implicit via re-request) |
| Binary data | No — text only | Yes | Yes |
| Best for | [LLM](../ai/generation/llm.md) token streaming, notifications, live feeds | Chat, multiplayer, anything needing client→server pushes too | Legacy fallback when neither is available |

Use SSE when data only needs to flow one way (server to client) — which is exactly the shape of streaming an [LLM](../ai/generation/llm.md)'s response token by token. Reach for [WebSockets](../networking/websockets.md) only when the client also needs to push data back over the same connection mid-stream (e.g. collaborative editing, voice/video signaling).

## Client Side: the `EventSource` API

Browsers have a built-in client for SSE that handles reconnection automatically:

```javascript
const source = new EventSource("/chat/stream?message=hello");

source.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.token);
};

source.addEventListener("done", () => {
  source.close();
});

source.onerror = () => {
  // EventSource reconnects automatically by default;
  // this fires on each dropped connection before it retries.
};
```

`EventSource` only supports `GET` requests and can't set custom headers (e.g. an `Authorization` bearer token) in most browsers, which is why many [LLM](../ai/generation/llm.md) chat UIs instead use `fetch()` with a `ReadableStream` reader to parse the `text/event-stream` body manually when auth headers are required — the wire format is the same, just consumed without the built-in `EventSource` object.

## Server Side: Streaming an LLM Response (FastAPI)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

async def event_stream(message: str):
    async for chunk in llm_client.stream_chat(message):
        yield f"data: {json.dumps({'token': chunk})}\n\n"
    yield "event: done\ndata: {}\n\n"

@app.get("/chat/stream")
async def chat_stream(message: str):
    return StreamingResponse(event_stream(message), media_type="text/event-stream")
```

This is why SSE pairs naturally with an [ASGI](../backend/architecture/asgi.md) server like Uvicorn: the endpoint is an `async` generator, and [the event loop](../programming/javascript/event-loop.md) keeps the connection open and flushes each `yield` to the client as it's produced, rather than buffering the whole response before sending it.

## Why This Matters for LLM Chat UIs

Generating a full [LLM](../ai/generation/llm.md) response can take several seconds. Waiting for the entire response before showing anything feels broken to a user; streaming each token as it's generated (the "typing" effect seen in ChatGPT-style UIs) is what SSE is commonly used for — the server pushes each token the moment the model produces it, and the client renders incrementally instead of waiting for a single large [JSON](../programming/fundamentals/json.md) response at the end.

## Limitations

- Text only — no native binary support (binary payloads must be base64-encoded, adding overhead)
- One-directional — the client can't send data back over the same connection (send follow-up input via a separate normal HTTP request)
- Browsers cap the number of concurrent `EventSource` connections per domain over HTTP/1.1 (typically 6) — HTTP/2 removes this limit by multiplexing

## Related Concepts

- [ASGI](../backend/architecture/asgi.md) — the async server interface that makes long-lived streaming connections practical in Python
- [REST](../backend/api/rest.md) — the conventional request/response model SSE deviates from for the response side
- [Pydantic AI](../ai/agents/pydantic-ai.md) — an agent framework whose streaming output (`run_stream`) is commonly exposed to clients over SSE
