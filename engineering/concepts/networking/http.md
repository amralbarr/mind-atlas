# HTTP (Hypertext Transfer Protocol)

The application-layer protocol nearly all web traffic runs on — a text-based (originally) request/response protocol: a client sends a request, a server sends back a response, and the connection has no memory of previous requests unless the application layers state on top (cookies, tokens).

## Request Structure

```http
GET /users/1 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJ...
Accept: application/json
```

| Part | Meaning |
|---|---|
| Method | The action being requested (see below) |
| Path | Which resource |
| Headers | Metadata about the request (auth, content type, caching hints) |
| Body (optional) | Data being sent — present on `POST`/`PUT`/`PATCH`, absent on `GET`/`DELETE` by convention |

## Common Methods

| Method | Purpose | Idempotent? | Has a body? |
|---|---|---|---|
| `GET` | Retrieve a resource | Yes | No |
| `POST` | Create a resource / trigger an action | No | Yes |
| `PUT` | Replace a resource entirely | Yes | Yes |
| `PATCH` | Partially update a resource | No (usually) | Yes |
| `DELETE` | Remove a resource | Yes | No (usually) |

**Idempotent** means calling it once vs. many times with the same input produces the same end state — calling `DELETE /users/1` five times leaves the same result as calling it once (the user is gone); calling `POST /users` five times typically creates five users. This matters directly for retry safety: a client can safely retry an idempotent request after a timeout without knowing whether the first attempt succeeded, but retrying a non-idempotent request risks duplicating the effect — see [Idempotency & Race Conditions](../programming/fundamentals/idempotency-and-race-conditions.md).

## HTTP Is Stateless

Each request is independent — the server retains no memory of a "session" between requests unless the application explicitly implements one (a cookie holding a session id, a bearer token in an `Authorization` header). This is a deliberate simplicity/scalability trade-off: a stateless protocol means any server behind a load balancer can handle any request, with no need to route a client back to "the same server it talked to last time."

## HTTP/1.1 vs. HTTP/2 vs. HTTP/3

| | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| Format | Text-based | Binary, multiplexed | Binary, multiplexed |
| Connections per host | Multiple parallel [TCP](tcp.md) connections needed to avoid head-of-line blocking | One [TCP](tcp.md) connection, many concurrent streams | One QUIC (UDP-based) connection |
| Head-of-line blocking | Yes, per connection | Reduced (multiplexed streams) | Eliminated (QUIC handles stream loss independently) |
| Typical use today | Still common, universally supported | Widely deployed default on modern servers/CDNs | Growing adoption, especially for latency-sensitive traffic |

The practical takeaway: HTTP/2+ lets a browser fetch many resources over one connection efficiently, which is part of why bundler/build tooling advice from the HTTP/1.1 era (aggressively concatenating every asset into one file to minimize connections) matters less on modern infrastructure.

## HTTP vs. HTTPS

Plain HTTP sends everything — headers, body, cookies — as cleartext, readable by anyone on the network path. See [HTTPS](https.md) for how [TLS](tls.md) encryption fixes this without changing HTTP's own request/response model at all — [HTTPS](https.md) is HTTP running over an encrypted [TLS](tls.md) connection, not a different protocol.

## Common Questions

**Why does `GET` never have a body, technically speaking?**
> The HTTP spec doesn't strictly forbid a body on `GET`, but it defines no semantics for it, and many servers, proxies, and caches ignore or strip it — the safe, portable convention is to put all request data for a `GET` into the URL (path/query params) instead.

**What's the difference between `PUT` and `PATCH`?**
> `PUT` conceptually replaces the entire resource with what's sent (fields omitted are implicitly cleared); `PATCH` applies a partial update (only the fields sent are changed). In practice many APIs use `PATCH` loosely for partial updates and never implement true `PUT` semantics — worth confirming per-API rather than assuming.

## Related

- [HTTPS](https.md)
- [HTTP Status Codes](../backend/api/http-status-codes.md)
- [REST](../backend/api/rest.md)
- [DNS](dns.md)
- [TCP](tcp.md)
- [WebSockets](websockets.md)
- [Reverse Proxy](reverse-proxy.md)
- [curl Commands](../../commands/curl.md)
