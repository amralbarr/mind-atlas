# Backend For Frontend (BFF)

**BFF (Backend For Frontend)** is an architecture pattern where a dedicated backend is built for each frontend client (web, mobile, admin, etc.), instead of a single generic backend serving every client.

## Core Idea

Instead of:

```text
Frontend (Web + Mobile) → One Generic API → Services
```

you have:

```text
Web App     → Web BFF     → Services
Mobile App  → Mobile BFF  → Services
Admin Panel → Admin BFF   → Services
```

Each frontend gets a backend tailored to its exact needs.

## Why BFF Exists

Different frontends need different data shapes, different performance characteristics, and sometimes different [authentication](../../security/auth/authentication.md) logic. A single shared API trying to serve all of them tends to become too complex, prone to over-fetching or under-fetching, and hard to maintain.

## Example

### Without a BFF

A mobile client has to make several round trips:

```text
GET /user
GET /orders
GET /notifications
```

Too many requests for a mobile connection.

### With a BFF

The mobile client makes one call:

```text
GET /mobile/dashboard
```

The BFF aggregates the underlying services, formats the response, and returns exactly what the mobile client needs — faster and simpler.

## What a BFF Does

- Aggregates multiple backend services into one response.
- Transforms data into the shape the UI needs.
- Handles frontend-specific logic (e.g. formatting, auth flow differences).
- Reduces the number of round-trip API calls.

## Example Flow

```text
Mobile App → Mobile BFF → (User Service + Orders Service + AI Service + DB)
```

## BFF vs. API Gateway

| Feature | API Gateway | BFF |
|---|---|---|
| Purpose | Routing & security | Tailored backend logic |
| Logic | Minimal | High (UI-specific) |
| Per-frontend | No | Yes |

The two are often used together rather than as alternatives: an API Gateway handles cross-cutting routing and security, while a BFF sits behind it shaping data per client.

## Example: Multi-Client Platform

**Web BFF** — returns a full dashboard payload, including charts, logs, and configuration.

**Mobile BFF** — returns compact data, optimized for speed, with fewer fields.

**Agent/service BFF** (optional) — aggregates results from several backend services (e.g. [OCR](../../ai/ingestion/ocr.md), an [LLM](../../ai/generation/llm.md), and text-to-speech) into one response for a specialized client.

## Advantages

- Better performance per client.
- Cleaner frontend code (no client-side aggregation).
- Flexible evolution — each BFF can change independently.
- Easier scaling per frontend.

## Challenges

- More services to build and maintain.
- Possible logic duplication across BFFs.
- Requires a well-thought-out structure to avoid becoming a dumping ground.

## One-Line Definition

> BFF is a custom backend layer built specifically for one frontend client.

## When to Use It

Use a BFF when:

- There are multiple frontends (web, mobile, admin, etc.).
- A shared API is becoming messy or overloaded with conditional logic.
- Each UI needs an optimized, purpose-built response shape.

## Related

- [Monolith vs Microservices](monolith-vs-microservices.md)
- [System Design](system-design.md)
- [REST](../api/rest.md)
- [Mesh Architecture](../../distributed-systems/patterns/mesh-architecture.md)
