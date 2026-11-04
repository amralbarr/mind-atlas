# Consul

HashiCorp Consul is a service registry, health-checking system, and key-value config store combined — services register themselves (or are registered by an agent) on startup, other services discover them by name instead of a hardcoded address, and Consul continuously health-checks each registered instance so failed ones drop out of discovery automatically. See [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md#service-discovery) for how this fits alongside the other pieces of a microservices system.

## Core Concepts

| Term | Meaning |
|---|---|
| **Service registration** | A service instance announces itself to Consul (name, address, port, health check) |
| **Health check** | Consul periodically verifies a registered instance is actually alive ([HTTP](../../networking/http.md) ping, [TCP](../../networking/tcp.md) connect, script, or a service-reported TTL) — unhealthy instances are excluded from discovery results, not just left listed |
| **[DNS](../../networking/dns.md)/[HTTP](../../networking/http.md) interface** | Other services can resolve `orders-service.service.consul` via [DNS](../../networking/dns.md), or query Consul's [HTTP](../../networking/http.md) API directly, to get a list of healthy instances |
| **KV store** | A hierarchical key-value store bundled into the same Consul agent — commonly used for centralized, environment-specific config, separate from service discovery |
| **Consul Connect** | Consul's built-in service mesh capability (mTLS, sidecar proxies) — an optional layer beyond plain discovery |

## Running It (Docker, Dev Mode)

```bash
docker run -d --name consul -p 8500:8500 -p 8600:8600/udp \
  consul agent -dev -client=0.0.0.0
```

`8500` serves the [HTTP](../../networking/http.md) API/UI (`http://localhost:8500`); `8600` serves [DNS](../../networking/dns.md). `-dev` mode is single-node and non-persistent — fine for local development, not for production.

## Registering a Service

```json
// orders-service.json
{
  "service": {
    "name": "orders-service",
    "port": 3000,
    "check": {
      "http": "http://localhost:3000/health",
      "interval": "10s"
    }
  }
}
```

```bash
consul services register orders-service.json
```

## Discovering a Service (DNS or HTTP)

```bash
# DNS lookup — returns healthy instances only
dig @127.0.0.1 -p 8600 orders-service.service.consul

# HTTP API equivalent
curl http://localhost:8500/v1/health/service/orders-service?passing
```

## Storing Config in the KV Store

```bash
consul kv put config/orders-service/database_url "postgres://db:5432/orders"
consul kv get config/orders-service/database_url
```

## Common Questions

**How does Consul compare to [Kubernetes](../../distributed-systems/kubernetes/ingress.md)' own built-in service discovery?**
> If a system already runs entirely on [Kubernetes](../../distributed-systems/kubernetes/ingress.md), its native Service/[DNS](../../networking/dns.md) mechanism handles the same problem without an extra component — see [Kubernetes Basics](../../distributed-systems/kubernetes/kubernetes-basics.md). Consul earns its place in non-[Kubernetes](../../distributed-systems/kubernetes/ingress.md) environments (VMs, bare metal, mixed infrastructure), or when its extra capabilities (multi-datacenter federation, Consul Connect service mesh, the bundled KV store) are specifically needed.

**Is Consul the same kind of tool as [Eureka](eureka.md)?**
> They solve the same core problem (service discovery), but Consul is broader — health checking, a KV store, multi-datacenter support, and an optional service mesh are all bundled in, whereas [Eureka](eureka.md) is a more narrowly scoped registry historically tied to the Netflix/Spring Cloud ecosystem.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Eureka](eureka.md)
- [Kubernetes Basics](../../distributed-systems/kubernetes/kubernetes-basics.md)
- [Secrets Management](../../security/secrets/secrets-management.md)
- [curl Commands](../../../commands/curl.md)
