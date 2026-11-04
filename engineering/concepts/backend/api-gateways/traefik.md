# Traefik

Traefik is a [reverse proxy](../../networking/reverse-proxy.md) / [API gateway](../../../overviews/backend/microservices-tech-stack.md#api-gateway) built around automatic service discovery — instead of hand-writing routing config, Traefik watches [Docker](../../containers/docker.md), [Kubernetes](../../distributed-systems/kubernetes/ingress.md), or other providers directly and derives its routing rules from labels/annotations already attached to your running containers.

## Core Concepts

| Term | Meaning |
|---|---|
| **Provider** | The source Traefik watches for services and routing config — [Docker](../../containers/docker.md), [Kubernetes](../../distributed-systems/kubernetes/ingress.md) ([Ingress](../../distributed-systems/kubernetes/ingress.md) or its own CRDs), [Consul](../service-discovery/consul.md), files, and more |
| **Router** | Matches an incoming request (by host, path, headers) and sends it to a Service |
| **Service** | The actual backend(s) a router forwards matched requests to |
| **[Middleware](../middleware.md)** | A pluggable request/response transform chained onto a router — auth, [rate limiting](../architecture/rate-limiting.md), redirects, header manipulation |
| **EntryPoint** | A listening port (e.g. `web` on 80, `websecure` on 443) that routers attach to |

## Docker Labels Drive Routing

```yaml
# docker-compose.yml
services:
  traefik:
    image: traefik:v3.0
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  orders-service:
    image: my-org/orders-service:latest
    labels:
      - "traefik.http.routers.orders.rule=PathPrefix(`/orders`)"
      - "traefik.http.services.orders.loadbalancer.server.port=3000"
```

No separate Traefik config file needs updating when `orders-service` is added, scaled, or removed — Traefik reads the labels directly off the running container and updates routing live.

## Automatic HTTPS (Let's Encrypt)

```yaml
command:
  - "--certificatesresolvers.myresolver.acme.httpchallenge=true"
  - "--certificatesresolvers.myresolver.acme.email=admin@example.com"
  - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
labels:
  - "traefik.http.routers.orders.tls.certresolver=myresolver"
```

Traefik requests and renews [TLS](../../networking/tls.md) certificates automatically per router, removing the manual certbot-and-cron-job workflow a plain [NGINX](nginx.md) setup would otherwise need.

## Common Questions

**Why choose Traefik over [Kong](kong.md) or [NGINX](nginx.md) for a [Docker](../../containers/docker.md)/[Kubernetes](../../distributed-systems/kubernetes/ingress.md)-based system?**
> When the priority is zero-touch routing that stays correct as services scale up/down or get rescheduled — Traefik's label/annotation-driven discovery removes the step of manually updating gateway config every time the service topology changes, which [Kong](kong.md) and [NGINX](nginx.md) don't do natively ([Kong](kong.md) needs its Admin API/declarative config updated; [NGINX](nginx.md) needs a config reload).

**Does Traefik replace [Kubernetes](../../distributed-systems/kubernetes/ingress.md)' own [Ingress](../../distributed-systems/kubernetes/ingress.md) controller concept?**
> Traefik commonly *is* the [Ingress](../../distributed-systems/kubernetes/ingress.md) controller in a [Kubernetes](../../distributed-systems/kubernetes/ingress.md) cluster — it implements the standard [Ingress](../../distributed-systems/kubernetes/ingress.md) resource, plus its own more expressive CRDs (`IngressRoute`) for finer control than plain [Ingress](../../distributed-systems/kubernetes/ingress.md) allows. See [Ingress](../../distributed-systems/kubernetes/ingress.md) for the underlying [Kubernetes](../../distributed-systems/kubernetes/ingress.md) concept.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Kong](kong.md)
- [NGINX](nginx.md)
- [Ingress](../../distributed-systems/kubernetes/ingress.md)
- [Reverse Proxy](../../networking/reverse-proxy.md)
- [Load Balancing](../../networking/load-balancing.md)
