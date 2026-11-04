# Ingress (Kubernetes)

**Ingress** is the Kubernetes component that controls how external traffic ([HTTP](../../networking/http.md)/[HTTPS](../../networking/https.md)) reaches services inside a cluster.

## Simple Idea

Without Ingress:

```text
User → NodePort / LoadBalancer → Service → Pods
```

With Ingress:

```text
User → Ingress → Service → Pods
```

It acts as a smart gateway, or [reverse proxy](../../networking/reverse-proxy.md), for the cluster.

## What Ingress Does

- Routes traffic based on domain.
- Routes traffic based on path.
- Handles SSL/[HTTPS](../../networking/https.md) termination.
- Centralizes external access into one entry point.

## Example

Given multiple services behind different subdomains:

- `api.example.com` → API service
- `ai.example.com` → AI service
- `app.example.com` → Frontend service

Ingress routes each hostname to the matching service:

```text
api.example.com → API Service
ai.example.com  → AI Service
app.example.com → Frontend Service
```

## Key Components

### Ingress Resource

The [YAML](../../devops/yaml.md) configuration that defines routing rules.

### Ingress Controller

The actual engine that applies those rules. Popular [controllers](../../backend/nestjs/controllers.md) include the [NGINX](../../backend/api-gateways/nginx.md) Ingress Controller and [Traefik](../../backend/api-gateways/traefik.md).

## Example YAML

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
```

This routes `api.example.com` to the `api-service`.

## HTTPS (SSL)

Ingress can terminate SSL/[HTTPS](../../networking/https.md) and manage certificates (e.g. via Let's Encrypt).

## Ingress vs. Service

| Feature | Service | Ingress |
|---|---|---|
| Internal routing | Yes | No |
| External access | Limited | Yes |
| Domain-based routing | No | Yes |
| Path-based routing | No | Yes |

## Relation to a Traditional Reverse Proxy

For a system already running behind [Nginx](../../backend/api-gateways/nginx.md) with domain-based reverse proxying, Ingress serves the same purpose inside a Kubernetes cluster — it effectively replaces the [Nginx](../../backend/api-gateways/nginx.md) configuration layer with a Kubernetes-native equivalent.

## One-Line Definition

> Ingress is the entry point that routes external traffic into Kubernetes services.

## Related

- [Kubernetes Basics](kubernetes-basics.md)
- [Mesh Architecture](../patterns/mesh-architecture.md)
- [HTTPS](../../networking/https.md)
