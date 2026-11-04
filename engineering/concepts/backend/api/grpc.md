# gRPC

gRPC (gRPC Remote Procedure Call) is a high-performance RPC framework, originally built by Google, for calling a method on a remote service as if it were a local function call. It runs over [HTTP/2](../../networking/http.md) and uses Protocol Buffers (protobuf) as its wire format — a binary [serialization](../../programming/fundamentals/serialization.md) that's smaller and faster to parse than [JSON](../../programming/fundamentals/json.md).

## Contract-First: The `.proto` File

Unlike [REST](rest.md), where the "contract" is usually informal (documented endpoints and [JSON](../../programming/fundamentals/json.md) shapes), gRPC starts from a strongly typed schema that both client and server generate code from:

```proto
syntax = "proto3";

service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
  rpc ListUsers (ListUsersRequest) returns (stream User);
}

message UserRequest {
  int32 id = 1;
}

message UserResponse {
  int32 id = 1;
  string name = 2;
  string email = 3;
}
```

A code generator (`protoc`) turns this `.proto` file into client and server stubs in whichever language each side is written in — the client calls `client.GetUser(request)` and it looks like an ordinary function call, but under the hood it serializes the request to protobuf, sends it over [HTTP](../../networking/http.md)/2, and deserializes the response.

## Why Binary + HTTP/2 Matters

| | [JSON](../../programming/fundamentals/json.md) over [HTTP](../../networking/http.md)/1.1 (typical [REST](rest.md)) | Protobuf over [HTTP](../../networking/http.md)/2 (gRPC) |
|---|---|---|
| Payload format | Text, human-readable, larger | Binary, compact, not human-readable |
| Parsing cost | Higher — text parsing, dynamic typing | Lower — binary is faster to serialize/deserialize |
| Connection reuse | One request per connection in [HTTP](../../networking/http.md)/1.1 (or pipelining workarounds) | [HTTP](../../networking/http.md)/2 multiplexes many concurrent calls over a single [TCP](../../networking/tcp.md) connection |
| Typing | Whatever the client assumes about the [JSON](../../programming/fundamentals/json.md) shape | Enforced by the generated code on both sides at compile time |

The combination is why gRPC is a common choice for internal service-to-service calls where every millisecond and byte matters at high volume, and where both ends of the call are code you control (so generating stubs from a shared `.proto` file is practical).

## The Four Call Types

gRPC supports more than simple request/response, taking advantage of [HTTP](../../networking/http.md)/2's native support for concurrent, bidirectional streams over one connection:

| Type | Shape | Example use |
|---|---|---|
| **Unary** | One request → one response | `GetUser(id)` — the [REST](rest.md)-equivalent case |
| **Server streaming** | One request → a stream of responses | Subscribing to price updates for one stock |
| **Client streaming** | A stream of requests → one response | Uploading a large file in chunks, server acks once at the end |
| **Bidirectional streaming** | Both sides stream independently | A live chat or collaborative-editing channel over one call |

```proto
rpc WatchOrders (OrderFilter) returns (stream OrderUpdate);   // server streaming
rpc UploadChunks (stream FileChunk) returns (UploadResult);    // client streaming
rpc Chat (stream Message) returns (stream Message);             // bidirectional
```

## gRPC vs. REST

| | [REST](rest.md) | gRPC |
|---|---|---|
| Payload | [JSON](../../programming/fundamentals/json.md) (text) | Protobuf (binary) |
| Contract | Informal / [OpenAPI](openapi.md) spec (often written after the fact) | Formal `.proto` schema, code-generated, enforced at compile time |
| Browser support | Native (`fetch`) | Not directly — browsers can't speak raw [HTTP](../../networking/http.md)/2 trailers the way gRPC needs; requires gRPC-Web plus a proxy translation layer |
| Human-readable/debuggable | Yes — inspect with curl, browser devtools | No — needs dedicated tooling (`grpcurl`, BloomRPC) to inspect calls |
| Streaming | Awkward ([SSE](../../protocols/sse.md)/[WebSockets](../../networking/websockets.md) bolted on) | Native, in all four directions listed above |
| Best for | Public APIs, browser clients, simple CRUD | Internal microservice-to-microservice calls, high-throughput/low-latency paths |

## gRPC vs. GraphQL

A different axis of comparison — [REST](rest.md) and gRPC are both "call a defined operation," while [GraphQL](graphql.md) lets the client shape the response. gRPC and [GraphQL](graphql.md) are rarely direct competitors in practice: gRPC dominates internal backend-to-backend traffic, [GraphQL](graphql.md) is aimed at the client-facing aggregation layer, and a system can reasonably use both — gRPC between its own services, [GraphQL](graphql.md) (or [REST](rest.md)) facing the browser/mobile client.

## Why gRPC Doesn't Replace REST at the Edge

Because browsers can't easily speak gRPC directly (no native binary-HTTP/2-trailer support in `fetch`), and because gRPC's binary payloads aren't debuggable with a browser's network tab or a plain `curl`, most systems keep a [REST](rest.md) (or [GraphQL](graphql.md)) layer facing the public internet/browser and use gRPC specifically for the internal, backend-to-backend hops where both ends are trusted, generated code:

```text
Browser → REST/GraphQL API → gRPC → Internal Service A → gRPC → Internal Service B
```

## Common Questions

**Why is gRPC described as feeling like "calling a local function"?**
> Because the generated client stub exposes the remote method as an ordinary function/method call in your language (`client.GetUser(id)`) — the network call, [serialization](../../programming/fundamentals/serialization.md), and deserialization are all hidden behind that generated code, unlike [REST](rest.md) where you typically construct a URL and parse a [JSON](../../programming/fundamentals/json.md) body by hand (or via an HTTP client library).

**Can gRPC be called directly from a browser?**
> Not the raw protocol — browsers lack the low-level HTTP/2 control gRPC needs. **gRPC-Web** is a JavaScript-compatible variant that requires a proxy (e.g. Envoy) to translate between gRPC-Web and true gRPC on the backend.

**Is gRPC always faster than REST in practice?**
> For high-volume, low-latency internal calls, generally yes, due to binary [serialization](../../programming/fundamentals/serialization.md) and HTTP/2 multiplexing. For low-volume or debugging-heavy scenarios, the performance gain often isn't worth the loss of human-readability and the added tooling/build-step complexity of maintaining `.proto` schemas and codegen.

## Related

- [API](api.md) — the general contract concept gRPC is one style of implementing
- [REST](rest.md)
- [GraphQL](graphql.md)
- [WebSockets](../../networking/websockets.md)
- [Server-Sent Events (SSE)](../../protocols/sse.md)
