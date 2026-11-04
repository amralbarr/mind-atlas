# Reverse Proxy

A reverse proxy sits in front of one or more backend servers and forwards client requests to them, returning the backend's response as if it came from the proxy itself — the client only ever talks to the proxy and never knows (or needs to know) which actual backend served the request.

```text
Client → Reverse Proxy → Backend Server(s)
```

## Reverse Proxy vs. Forward Proxy

These are frequently confused because both are "a proxy," but they sit on opposite sides of the connection and protect opposite parties:

| | Forward Proxy | Reverse Proxy |
|---|---|---|
| Sits in front of | The **client** | The **server** |
| Hides | The client's identity from the server | The server's identity/topology from the client |
| Client is aware of it? | Yes — the client is explicitly configured to use it | No — from the client's perspective, it *is* the server |
| Classic example | A corporate proxy that all employee traffic routes through before reaching the internet | [NGINX](../backend/api-gateways/nginx.md)/[Kong](../backend/api-gateways/kong.md)/[Traefik](../backend/api-gateways/traefik.md) sitting in front of an API |
| Typical purpose | Content filtering, anonymizing outbound requests, caching for a group of clients | [Load balancing](load-balancing.md), [TLS](tls.md) termination, routing, hiding internal architecture |

A simple way to remember it: a forward proxy works **on behalf of clients** reaching out to the internet; a reverse proxy works **on behalf of servers** receiving traffic from the internet.

## What a Reverse Proxy Actually Does

| Responsibility | Why it belongs at this layer |
|---|---|
| **Request routing** | Forwards `/orders` to the orders service, `/users` to the users service — one public entry point, many internal services |
| **[Load balancing](load-balancing.md)** | Distributes requests for one route across multiple backend instances |
| **[TLS](tls.md) termination** | Decrypts [HTTPS](https.md) once at the edge; internal traffic to backends can run plain [HTTP](http.md) inside a trusted network, so backends don't each need their own certificate |
| **Caching** | Can cache responses for identical requests, serving repeat requests without hitting the backend at all |
| **Compression** | Gzip/Brotli-compresses responses before sending to the client, offloading that work from application servers |
| **Hiding internal topology** | Backend hostnames, ports, and internal network layout are never exposed to the client — only the proxy's public address is |
| **Centralized cross-cutting concerns** | [Rate limiting](../backend/architecture/rate-limiting.md), request logging, security headers, and auth-token parsing can live in one place instead of every backend service reimplementing them |

## A Minimal Example (NGINX)

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate     /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location /orders {
        proxy_pass http://orders-service:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

The client sends a request to `api.example.com`; [NGINX](../backend/api-gateways/nginx.md) terminates [TLS](tls.md) and forwards it, in plain [HTTP](http.md), to `orders-service:3000` — the client never sees that hostname at all. The `X-Forwarded-For` header is how the backend recovers the *original* client IP, since from the backend's point of view every request now appears to come from the proxy.

## Why Backends Shouldn't Be Exposed Directly

Putting a reverse proxy in front of application servers isn't just about routing convenience — it also means:

- The backend never needs to handle raw [TLS](tls.md) itself (one less thing every service must implement correctly).
- Internal service addresses/ports can change freely without breaking anything client-facing.
- A single choke point exists for adding security headers, [rate limiting](../backend/architecture/rate-limiting.md), or blocking malicious traffic, instead of duplicating that logic across every service.
- Scaling a backend (adding/removing instances) is invisible to clients — the proxy's [load-balancing](load-balancing.md) layer absorbs the change.

## Reverse Proxy vs. API Gateway

A plain reverse proxy (like a bare [NGINX](../backend/api-gateways/nginx.md) config) routes and load-balances but has no built-in concept of API consumers, auth plugins, or an admin API for dynamically managing routes. A purpose-built **API gateway** ([Kong](../backend/api-gateways/kong.md), [AWS API Gateway](../backend/api-gateways/aws-api-gateway.md)) is a reverse proxy with that extra product layer built on top — see [NGINX](../backend/api-gateways/nginx.md)'s own "Is [NGINX](../backend/api-gateways/nginx.md) itself an API gateway?" discussion for the full distinction, since gateways like [Kong](../backend/api-gateways/kong.md) are themselves frequently built *on top of* reverse-proxy engines like [NGINX](../backend/api-gateways/nginx.md)/OpenResty.

## Common Questions

**Is a [CDN](cdn.md) a kind of reverse proxy?**
> Conceptually yes — a [CDN](cdn.md) edge node accepts client requests and forwards (or serves from cache) on behalf of an origin server the client never talks to directly, which is the same reverse-proxy shape, just distributed geographically and optimized for caching static/cacheable content rather than routing to microservices.

**Does a reverse proxy always do [load balancing](load-balancing.md)?**
> No — a reverse proxy with only one backend does no [load balancing](load-balancing.md) at all; it's still a reverse proxy purely by virtue of forwarding on the backend's behalf. [Load balancing](load-balancing.md) is one *common* thing a reverse proxy does when there's more than one backend to choose from, not a defining property of the pattern itself.

**Why terminate [TLS](tls.md) at the reverse proxy instead of at each backend service?**
> Centralizing certificate management in one place (renewal, configuration, cipher policy) is simpler and less error-prone than distributing it across every service, and it lets internal traffic run as plain, slightly cheaper [HTTP](http.md) within a network boundary that's already trusted.

## Related

- [TLS](tls.md) — termination is one of the core jobs a reverse proxy centralizes
- [Load Balancing](load-balancing.md)
- [NGINX](../backend/api-gateways/nginx.md)
- [Kong](../backend/api-gateways/kong.md)
- [Traefik](../backend/api-gateways/traefik.md)
- [CDN](cdn.md)
- [HTTPS](https.md)
