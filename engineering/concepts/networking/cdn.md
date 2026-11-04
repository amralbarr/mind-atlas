# CDN (Content Delivery Network)

## What Is a CDN?

A CDN is a network of servers, distributed globally, that cache and deliver files (images, videos, static assets, and sometimes API responses) from the location closest to the requesting user.

## Why Use a CDN?

Without a CDN, every request travels all the way to your origin server, which may be far from the user and slow. With a CDN, the request is served from the nearest edge server, which is fast and reduces load on the origin entirely.

## What Does a CDN Cache?

- Images
- Videos
- PDFs and other static files
- Static JS/CSS bundles
- API responses (optional, depending on cache rules)

## The Three Layers

It helps to think of a CDN-backed delivery pipeline as three layers working together, not as one single thing:

| Component      | Role                          | Example                  |
| ---------------- | -------------------------------- | ---------------------------- |
| **Storage**         | where files actually live            | Amazon S3, MinIO, local disk    |
| **Origin server**       | [authentication](../security/auth/authentication.md), APIs, business logic   | NestJS, Node.js, [Django](../programming/python/django.md)            |
| **CDN**                    | caches and serves files close to the user   | Cloudflare, Amazon CloudFront          |

## Common Architectures

### 1. Cloud Storage + CDN (recommended for most production systems)

```text
User → CDN (Cloudflare) → Storage (S3)
```

Flow:

1. User requests a file.
2. The CDN checks its cache.
3. If not cached, the CDN fetches it from storage (e.g. S3) and caches it.
4. The next user gets it instantly from the CDN's cache.

Pros: very fast globally, highly scalable, no load on your own server, reliable.
Cons: a small ongoing cost, and some initial setup.

### 2. Local/Origin Server + CDN

```text
User → CDN (Cloudflare) → Origin server (Nginx) → local /uploads
```

Flow: files are uploaded and stored on local disk, the CDN caches responses from the origin server, and most subsequent requests hit the CDN before ever reaching the origin.

Pros: full control, cheap for small systems.
Cons: the origin server can become a bottleneck, and it scales worse than cloud storage.

### 3. Self-Hosted Object Storage + CDN (e.g. MinIO)

```text
User → CDN (Cloudflare) → MinIO → Server (API only, e.g. NestJS)
```

Same shape as the S3 setup, but with a self-hosted, S3-compatible object store (MinIO) instead of a managed cloud service — useful when data has to stay on infrastructure you control. See [Object Storage](../cloud/infrastructure/object-storage.md) for more on this layer.

### Quick Comparison

| Feature        | Cloud Storage + CDN | Origin Server + CDN |
| ---------------- | ---------------------- | ------------------------ |
| Speed                | Excellent                 | Good                          |
| Scalability             | Excellent                    | Limited                             |
| Cost                       | Medium                          | Low                                     |
| Maintenance                    | Low                                | High                                        |

### When to Use What

- Small project → origin server + CDN.
- Startup / scaling → cloud storage + CDN.
- Large system → cloud storage + CDN (effectively required at scale).

## How the Backend Should Use a CDN

**Upload flow** — the client uploads through the API server, which writes to storage and returns a URL:

```js
POST /upload
→ server saves to S3 / MinIO
→ returns URL
```

**Access flow (read path)** — files should be read through the CDN, not proxied through the application server:

```text
Wrong:   User → Server → Storage
Correct: User → CDN → Storage
```

The server's job is to serve logic (APIs); the CDN's job is to serve files. Mixing the two turns the application server into an avoidable bottleneck.

## URL Strategy

Serve cached assets from a dedicated CDN-fronted host rather than from the API host:

```text
Good: https://cdn.yoursite.com/images/img1.jpg
Bad:  https://api.yoursite.com/uploads/img1.jpg
```

## Common Mistakes

- Serving images/files directly from the backend application server.
- Skipping the CDN entirely, which hurts global latency.
- Mixing file delivery and API logic on the same host.
- Not defining explicit caching rules for cached content.

## Example: Full Stack Wiring

A typical production wiring for a system with a Next.js frontend, [object storage](../cloud/infrastructure/object-storage.md), and an API backend:

```text
Frontend (Next.js)
   ↓
CDN (Cloudflare)
   ↓
Storage (S3 / MinIO)
   ↓
API server (NestJS) — logic only, no file serving
```

## Related

- [DNS](dns.md)
- [HTTP](http.md)
- [Object Storage](../cloud/infrastructure/object-storage.md)
- [Reverse Proxy](reverse-proxy.md)
- [Load Balancing](load-balancing.md)
- [Caching Strategies](../backend/architecture/caching-strategies.md)
- [Cloudflare Tunnel (`cloudflared`) Commands](../../commands/cloudflare-tunnel.md) — for the "Origin Server + CDN" architecture above, a Tunnel lets the CDN reach the origin without ever exposing the origin's IP publicly
