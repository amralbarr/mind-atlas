# Kong

Kong is a popular open-source [API gateway](../../../overviews/backend/microservices-tech-stack.md#api-gateway) built on top of [NGINX](nginx.md)/OpenResty — a single entry point in front of a microservices system, extended through a plugin architecture rather than custom code for cross-cutting concerns like auth, [rate limiting](../architecture/rate-limiting.md), and transformations.

## Core Concepts

| Term | Meaning |
|---|---|
| **Service** | An upstream API/microservice Kong proxies to |
| **Route** | A rule mapping incoming requests (by path, host, method) to a Service |
| **Plugin** | A pluggable unit of functionality (auth, [rate limiting](../architecture/rate-limiting.md), logging, request/response transformation) attached to a Service, Route, or globally |
| **Consumer** | An identity (an API client, a partner, an end user) that plugins like auth/rate-limiting can apply rules to individually |
| **Upstream** | A named virtual host representing a load-balanced pool of target servers for a Service |

## Running It (Docker, DB-less mode)

```bash
docker run -d --name kong \
  -e "KONG_DATABASE=off" \
  -e "KONG_DECLARATIVE_CONFIG=/kong.yml" \
  -v $(pwd)/kong.yml:/kong.yml \
  -p 8000:8000 -p 8001:8001 \
  kong:latest
```

`8000` is the proxy port clients hit; `8001` is the Admin API used to configure Kong itself. DB-less mode reads all configuration from a declarative [YAML](../../devops/yaml.md) file — no separate Postgres/[Cassandra](../../databases/nosql/cassandra.md) needed, a common choice for GitOps-style config management.

## Declarative Configuration

```yaml
# kong.yml
_format_version: "3.0"
services:
  - name: orders-service
    url: http://orders-service:3000
    routes:
      - name: orders-route
        paths: ["/orders"]
    plugins:
      - name: rate-limiting
        config:
          minute: 100
      - name: key-auth
```

Any request to `/orders` is routed to `orders-service`, rate-limited to 100/minute, and requires an [API key](../../security/auth/api-key.md) — all declared once at the gateway, instead of every downstream service reimplementing auth and [rate limiting](../architecture/rate-limiting.md).

## Adding a Service via the Admin API

```bash
curl -i -X POST http://localhost:8001/services \
  --data name=orders-service \
  --data url=http://orders-service:3000

curl -i -X POST http://localhost:8001/services/orders-service/routes \
  --data paths[]=/orders
```

## Common Questions

**How does Kong differ from a plain [NGINX](nginx.md) [reverse proxy](../../networking/reverse-proxy.md)?**
> [NGINX](nginx.md) is a general-purpose [reverse proxy](../../networking/reverse-proxy.md) configured via a static config file/reload cycle. Kong is built specifically as an API gateway — it exposes a first-class Admin API/declarative config for services and routes, and its plugin ecosystem (auth, [rate limiting](../architecture/rate-limiting.md), transformations) is designed to be added per-route without writing custom [NGINX](nginx.md) config or Lua.

**When would [Traefik](traefik.md) be a better fit than Kong?**
> When most of the value needed is automatic service discovery in a [Docker](../../containers/docker.md)/[Kubernetes](../../distributed-systems/kubernetes/ingress.md) environment (labels/annotations driving routing) rather than a rich plugin ecosystem for API-specific concerns — see [Traefik](traefik.md).

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [NGINX](nginx.md)
- [Traefik](traefik.md)
- [AWS API Gateway](aws-api-gateway.md)
- [Reverse Proxy](../../networking/reverse-proxy.md)
- [Load Balancing](../../networking/load-balancing.md)
- [Rate Limiting](../architecture/rate-limiting.md)
- [API Versioning](../api/api-versioning.md)
- [curl Commands](../../../commands/curl.md)
