# Azure CDN

[Azure](azure.md) [CDN](../../networking/cdn.md) (Content Delivery Network) caches content at edge locations physically close to end users, so a request for a file doesn't have to travel all the way back to its origin storage on every single request. It's most commonly placed in front of [Azure Blob Storage](azure-blob-storage.md) to serve static assets (images, videos, downloads, static website files) with lower latency and far less load on the origin storage account.

## How it fits in front of Blob Storage

```
User request
    ↓
Azure CDN edge node (geographically close to the user)
    ↓ (cache miss only)
Azure Blob Storage (the origin — the actual source of truth)
```

The first request for a given file is a **cache miss** — the [CDN](../../networking/cdn.md) edge node fetches it from the Blob Storage origin, serves it to the user, and caches a copy. Every subsequent request for that same file, from any user near that edge node, is served directly from the cache — never touching the origin storage account at all, which is both faster for the user and cheaper (fewer transactions and less egress bandwidth against the storage account).

## Core concepts

| Term | Meaning |
|---|---|
| **Origin** | Where the [CDN](../../networking/cdn.md) fetches content from on a cache miss — typically an [Azure Blob Storage](azure-blob-storage.md) container, but can be any publicly reachable [HTTP](../../networking/http.md)(S) endpoint |
| **Edge node (POP)** | A geographically distributed cache server — the actual location a user's request is served from |
| **Cache rule** | Controls how long content stays cached (TTL) and under what conditions it's considered stale |
| **Purge** | Manually invalidating cached content at all edge nodes — needed when an origin file changes and you can't wait for the TTL to expire naturally |
| **Custom domain + [HTTPS](../../networking/https.md)** | Serving [CDN](../../networking/cdn.md) content under your own domain name with a managed or custom [TLS](../../networking/tls.md) certificate, instead of the default [Azure](azure.md)-provided hostname |

## Why not just serve directly from Blob Storage?

Blob Storage alone is already reachable over [HTTPS](../../networking/https.md) and can serve static files directly — a [CDN](../../networking/cdn.md) isn't required to make files publicly accessible. What it adds is specifically about **scale and latency**: without a [CDN](../../networking/cdn.md), every single request — from anywhere in the world — hits the same storage account's network and incurs its egress cost; a global user base means a user far from the storage account's region pays that distance in latency on every request, not just the first one. A [CDN](../../networking/cdn.md) trades a layer of operational complexity (cache invalidation, purge timing) for meaningfully lower latency at scale and reduced direct load on the origin.

## Related

- [Azure Blob Storage](azure-blob-storage.md) — the most common origin a CDN sits in front of
- [ADLS](adls.md) — can also serve as a CDN origin, though it's less commonly fronted by a CDN than plain Blob Storage, since [ADLS](adls.md) workloads are typically analytical rather than public-content-serving
