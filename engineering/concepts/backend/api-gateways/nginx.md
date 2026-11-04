# NGINX

NGINX is a general-purpose, high-performance web server and [reverse proxy](../../networking/reverse-proxy.md) — commonly configured as an [API gateway](../../../overviews/backend/microservices-tech-stack.md#api-gateway), load balancer, or [TLS](../../networking/tls.md) termination point in front of a microservices system, without being purpose-built as a gateway product the way [Kong](kong.md) is.

## Core Concepts

| Term | Meaning |
|---|---|
| **Server block** | A virtual host — one `server {}` config handling requests for a given domain/port |
| **Location block** | A rule inside a server block matching a request path, deciding how it's handled (proxied, served as a static file, redirected) |
| **Upstream** | A named pool of backend servers NGINX load-balances requests across |
| **[Reverse proxy](../../networking/reverse-proxy.md)** | NGINX forwards a client request to an internal backend and returns the backend's response — the client only ever talks to NGINX |

## Reverse Proxy + Load Balancing Config

```nginx
upstream orders_backend {
    server orders-service-1:3000;
    server orders-service-2:3000;
}

server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate     /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location /orders {
        proxy_pass http://orders_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Requests to `/orders` are load-balanced (round-robin by default) across both backend instances; [TLS](../../networking/tls.md) is terminated at NGINX, so internal traffic to `orders-service-*` can run plain [HTTP](../../networking/http.md) inside a trusted network.

## Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    location /orders {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://orders_backend;
    }
}
```

## Reloading Config Without Downtime

```bash
nginx -t              # validate config before applying
nginx -s reload        # gracefully reload — existing connections finish, new ones use new config
```

## Common Questions

**Is NGINX itself "an API gateway"?**
> Not out of the box in the same sense as [Kong](kong.md) or [AWS API Gateway](aws-api-gateway.md) — it doesn't ship with built-in auth/rate-limiting plugins, a consumer model, or an admin API for dynamic route management. It's routing/proxying infrastructure flexible enough to be *configured into* a gateway role, which is exactly why purpose-built gateways like [Kong](kong.md) are themselves often built on top of NGINX/OpenResty.

**When is plain NGINX preferable to [Kong](kong.md) or [Traefik](traefik.md)?**
> When the routing rules are relatively static and the main need is [TLS](../../networking/tls.md) termination, [load balancing](../../networking/load-balancing.md), and basic reverse proxying — the operational simplicity of one config file/reload cycle can be preferable to running a full gateway product for a small number of services.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Kong](kong.md)
- [Traefik](traefik.md)
- [HTTPS](../../networking/https.md)
- [Reverse Proxy](../../networking/reverse-proxy.md)
- [Load Balancing](../../networking/load-balancing.md)
- [Rate Limiting](../architecture/rate-limiting.md)
