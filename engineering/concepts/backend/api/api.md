# API
(Application Programming Interface)

An **API** is a defined contract that lets one piece of software ask another to do something or hand over data, without either side needing to know how the other is actually implemented internally — only what requests it accepts and what responses it returns. A web API specifically exposes that contract over a network (usually [HTTP](../../networking/http.md)), so a client running anywhere can call a server it has never seen the source code of.

## The Core Idea: A Contract, Not an Implementation

```
Client                           API (the contract)                    Server
  │  "GET /users/42"        ─────────────────────────▶                   │
  │                                                     looks up user 42 │
  │  ◀─────────────────────  {"id": 42, "name": "Alice"}  ───────────────│
```

The client only needs to know the shape of the request and the shape of the response — not whether the server stores users in [PostgreSQL](../../databases/relational/postgresql.md), [MongoDB](../../databases/nosql/mongodb.md), or a flat file. This is what lets the server's internals change freely (swap the database, rewrite the business logic) without breaking any client, as long as the contract itself stays the same.

## API Styles Covered in This Handbook

"API" isn't one specific technology — it's a category, and several different styles implement the same core idea differently:

| Style | How it works | Best for |
|---|---|---|
| **[REST](rest.md)** | Resources identified by URLs, manipulated via [HTTP](../../networking/http.md) verbs (GET/POST/PUT/DELETE) | The default choice for most public/internal web APIs — simple, cacheable, widely understood |
| **[GraphQL](graphql.md)** | A single endpoint; the client specifies exactly which fields it wants in the query itself | Clients with varying data needs (mobile vs. web) that would otherwise need many different [REST](rest.md) endpoints |
| **[gRPC](grpc.md)** | A `.proto`-defined contract, code-generated clients/servers, binary wire format over [HTTP/2](../../networking/http.md) | Service-to-service calls inside a system where performance and strict typing matter more than human-readability |
| **[Webhooks](webhooks.md)** | The server calls *the client's* URL when an event happens, instead of the client polling | Event notification — "tell me when X happens" rather than "let me ask if X happened yet" |

See [REST](rest.md), [GraphQL](graphql.md), and [gRPC](grpc.md) for the full detail on each; [Webhooks](webhooks.md) for the inverted-direction pattern.

## What Every API Needs, Regardless of Style

- **[OpenAPI](openapi.md) / a schema** — a machine-readable description of the contract itself (endpoints, request/response shapes, types), so clients and documentation can be generated from one source of truth instead of drifting out of sync with hand-written docs.
- **[HTTP status codes](http-status-codes.md)** — a standard vocabulary for what happened (200 success, 404 not found, 401 unauthorized, 500 server error), so a client can react programmatically without parsing English error text.
- **[Pagination](pagination.md)** — any endpoint that can return an unbounded number of results needs a way to request them in pages, or a single call risks returning an unusably large (or crash-inducing) response.
- **[API Versioning](api-versioning.md)** — a plan for changing the contract over time without breaking every client that depends on the current shape.
- **[Idempotency](idempotency.md)** — a way to safely retry a request (e.g. after a timeout, without knowing if the first attempt actually succeeded) without accidentally performing the same action twice, such as double-charging a payment.
- **Validation** — rejecting a malformed request before it reaches business logic, typically via a schema/decorator library like [class-validator](class-validator.md) (NestJS) or [Pydantic](../../programming/python/pydantic.md) (Python); see the [Validation Libraries overview](../../../overviews/programming/validation-libraries.md) for the cross-language comparison.
- **[Authentication and authorization](../../security/auth/authentication.md)** — verifying who's calling, and what that caller is allowed to do, since an API that exposes application internals over a network is also exposing an attack surface if left unprotected.

## API Gateways — Fronting Many APIs With One Entry Point

At scale, a system often has many internal services, each with its own API — an [API gateway](../api-gateways/) (e.g. [Kong](../api-gateways/kong.md), [NGINX](../api-gateways/nginx.md), [AWS API Gateway](../api-gateways/aws-api-gateway.md)) sits in front of all of them as a single entry point, handling cross-cutting concerns (auth, [rate limiting](../architecture/rate-limiting.md), routing, request transformation) once instead of reimplementing them in every individual service's own API.

## Related

- [REST](rest.md) — the most common API style, resource/URL-based
- [GraphQL](graphql.md) — client-specified query shape over a single endpoint
- [gRPC](grpc.md) — contract-first, binary, high-performance service-to-service calls
- [Webhooks](webhooks.md) — the server-initiated, inverted-direction pattern
- [OpenAPI](openapi.md) — the machine-readable contract description most [REST](rest.md) APIs are documented with
- [HTTP Status Codes](http-status-codes.md)
- [Pagination](pagination.md)
- [API Versioning](api-versioning.md)
- [Idempotency & Double-Submit Prevention](idempotency.md)
- [class-validator](class-validator.md) — request validation in NestJS
- [Authentication](../../security/auth/authentication.md) / [Authorization](../../security/authorization/authorization.md) — who's calling, and what they're allowed to do
