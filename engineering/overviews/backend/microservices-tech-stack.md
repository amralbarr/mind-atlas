# Microservices Technology Stack

The common building blocks a real microservices architecture needs beyond "several small services talking over [HTTP](../../concepts/networking/http.md)" — most of the actual infrastructure complexity mentioned in [Monolith vs. Microservices](../../concepts/backend/architecture/monolith-vs-microservices.md) comes from these pieces.

```text
Client
  ↓
API Gateway  ──────────────►  Service Discovery
  ↓                                  ↑
 ├── Auth Service   ◄──────────────┐ │
 ├── User Service   ◄──────────────┼─┘
 ├── Order Service  ◄──────────────┘
 └── Payment Service
       │
       ├── Config Management (env-specific settings, secrets)
       ├── Message Broker (async events between services)
       └── Observability (logs, metrics, traces — every service reports here)
```

## API Gateway

A single entry point that sits in front of all services, so clients never talk to internal services directly.

| Responsibility | Why it lives at the gateway, not each service |
|---|---|
| Routing | One place to map external routes to internal services |
| [Authentication](../../concepts/security/auth/authentication.md) | Verify identity once, pass a trusted context downstream, instead of re-implementing auth in every service |
| [Rate limiting](../../concepts/backend/architecture/rate-limiting.md) | Protect the whole system from one client's excess, without every service reimplementing it |
| Request aggregation | Combine calls to multiple services into one response for the client (see [BFF](../../concepts/backend/architecture/bff.md) for a related pattern) |
| [TLS](../../concepts/networking/tls.md) termination | Decrypt [HTTPS](../../concepts/networking/https.md) once at the edge; internal traffic can run plain [HTTP](../../concepts/networking/http.md) inside a trusted network |

| Tool | Notes |
|---|---|
| **[Kong](../../concepts/backend/api-gateways/kong.md)** | Popular open-source gateway, plugin-based (auth, [rate limiting](../../concepts/backend/architecture/rate-limiting.md), transformations) |
| **[NGINX](../../concepts/backend/api-gateways/nginx.md)** | General-purpose [reverse proxy](../../concepts/networking/reverse-proxy.md), commonly configured as a gateway too |
| **[Traefik](../../concepts/backend/api-gateways/traefik.md)** | Auto-discovers services (especially in [Docker](../../concepts/containers/docker.md)/[Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md)), config via labels/annotations |
| **[AWS API Gateway](../../concepts/backend/api-gateways/aws-api-gateway.md)** | Fully managed, tightly integrated with Lambda and other [AWS](../../concepts/cloud/infrastructure/aws.md) services |
| **[Spring Cloud Gateway](../../concepts/backend/api-gateways/spring-cloud-gateway.md)** | JVM-ecosystem-native choice for Spring-based microservices |

## Service Discovery

In a system where service instances scale up/down and get rescheduled to different hosts constantly, a service can't just hardcode "call `10.0.0.5:8080`" — it needs to ask "where is the User Service *right now*?"

| Approach | How it works |
|---|---|
| **Client-side discovery** | The calling service queries a registry directly and picks an instance itself (e.g. Netflix [Eureka](../../concepts/backend/service-discovery/eureka.md) + client-side [load balancing](../../concepts/networking/load-balancing.md)) |
| **Server-side discovery** | The caller sends the request to a stable address (e.g. a [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md) Service), and something else (a proxy, the platform) resolves it to a live instance |

| Tool | Notes |
|---|---|
| **[Consul](../../concepts/backend/service-discovery/consul.md)** | Service registry + health checking + KV config store combined |
| **[Eureka](../../concepts/backend/service-discovery/eureka.md)** | Netflix's registry, common in Spring Cloud stacks |
| **[Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md) [DNS](../../concepts/networking/dns.md) / Services** | The most common answer today for anything already running on [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md) — service discovery is built into the platform, so a dedicated registry is often unnecessary (see [Kubernetes Basics](../../concepts/distributed-systems/kubernetes/kubernetes-basics.md)) |

## Service Mesh

A dedicated infrastructure layer (Istio, Linkerd) that handles service-to-service traffic concerns — mutual [TLS](../../concepts/networking/tls.md), retries, traffic splitting, observability — *without* changing each service's code, usually via a sidecar proxy per instance. See [Mesh Architecture](../../concepts/distributed-systems/patterns/mesh-architecture.md) for the full treatment — it's substantial enough to warrant its own note. Worth adding once service-to-service traffic management outgrows what the API gateway and client libraries handle on their own; overkill for a small number of services.

## Observability: Logs, Metrics, Traces

Debugging a single monolith often means reading one log file. Debugging microservices means correlating what happened across many services for one user request — which is why observability tooling isn't optional infrastructure for microservices, it's how failures become diagnosable at all.

| Pillar | Answers | Common tools |
|---|---|---|
| **Logging** | What happened, in detail, at a point in time? | [ELK/EFK Stack](../../concepts/backend/observability/elk-stack.md) ([Elasticsearch](../../concepts/databases/search/elasticsearch.md) + Logstash/Fluentd + Kibana), [Grafana Loki](../../concepts/backend/observability/grafana-loki.md) |
| **Metrics** | How is the system performing in aggregate, over time? | [Prometheus](../../concepts/backend/observability/prometheus.md) (collection/storage) + [Grafana](../../concepts/backend/observability/grafana.md) (dashboards/visualization) |
| **Tracing** | How did one request flow across every service it touched, and where did time go? | [Jaeger](../../concepts/backend/observability/jaeger.md), [Zipkin](../../concepts/backend/observability/zipkin.md) |
| **Instrumentation standard** | How do services emit all three consistently, without locking into one vendor's SDK | **[OpenTelemetry](../../concepts/backend/observability/opentelemetry.md)** — a vendor-neutral standard for generating logs/metrics/traces, exportable to [Jaeger](../../concepts/backend/observability/jaeger.md), [Prometheus](../../concepts/backend/observability/prometheus.md), or a commercial backend interchangeably |

A **trace** ties together every service call made while handling one request via a shared trace id, propagated through each service-to-service call — without that shared id, a slow or failing request across five services looks like five unrelated log entries with no way to connect them.

## Resilience Patterns

Distributed calls fail in ways a single-process function call never does — a downstream service can be slow, overloaded, or simply down, and calling it should not be allowed to cascade into total failure.

| Pattern | Problem it solves |
|---|---|
| **Circuit Breaker** | After repeated failures calling a service, stop trying for a cooldown period and fail fast instead — prevents a struggling downstream service from also taking down everything that calls it by piling up slow/hanging requests |
| **[Retry (with backoff)](../../concepts/backend/resilience/exponential-backoff-and-jitter.md)** | A transient failure (a brief network blip) often succeeds on a second attempt — retrying blindly and immediately, though, can worsen an already-overloaded downstream service |
| **Timeout** | Never wait indefinitely for a response — an unbounded wait on one slow dependency can exhaust a caller's own thread/[connection pool](../../concepts/databases/relational/connection-pooling.md) |
| **Bulkhead** | Isolate resources (thread pools, connection pools) per downstream dependency, so one failing dependency can't starve resources needed to call a different, healthy one |

| Tool | Notes |
|---|---|
| **[Resilience4j](../../concepts/backend/resilience/resilience4j.md)** | Modern JVM library implementing all of the above patterns |
| **[Hystrix](../../concepts/backend/resilience/hystrix.md)** | Netflix's original circuit-breaker library — now in maintenance mode, superseded by [Resilience4j](../../concepts/backend/resilience/resilience4j.md) |
| **[Polly](../../concepts/backend/resilience/polly.md)** | The .NET-ecosystem equivalent |

## Configuration & Secrets Management

Each service needs environment-specific config (database URLs, feature flags) and sensitive values (API keys, credentials) — hardcoding either into a container image defeats the point of building many independently-deployable services.

| Tool | Notes |
|---|---|
| **[Consul](../../concepts/backend/service-discovery/consul.md) KV** | Config storage, bundled into [Consul](../../concepts/backend/service-discovery/consul.md), often paired with [Consul](../../concepts/backend/service-discovery/consul.md)'s own service discovery |
| **[Spring Cloud Config](../../concepts/backend/data/spring-cloud-config.md)** | Centralized, Git-backed config server for Spring-based services |
| **[Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md) ConfigMaps** | Non-sensitive config, native to [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md) |
| **HashiCorp Vault / [OpenBao](../../concepts/security/secrets/openbao.md)** | The dedicated answer for actual secrets, not just config — see [Secrets Management](../../concepts/security/secrets/secrets-management.md) for the full comparison |

## Common Questions

**Does every microservices system need all of this from day one?**
> No — this is the toolkit that becomes necessary as the number of services and the traffic between them grows, not a checklist to implement before writing the first service. A 3-service system often doesn't need a service mesh or a dedicated config server; a 30-service system usually can't operate without at least discovery, a gateway, and real observability.

**What's the actual difference between the API gateway and a service mesh — don't they overlap?**
> The gateway handles **north-south** traffic (external clients calling into the system); a service mesh handles **east-west** traffic (services calling each other internally). A system can have one without the other — a gateway alone is often enough until internal service-to-service traffic itself needs the mesh's retry/mTLS/observability features applied uniformly.

## Related

- [Monolith vs. Microservices](../../concepts/backend/architecture/monolith-vs-microservices.md)
- [Mesh Architecture](../../concepts/distributed-systems/patterns/mesh-architecture.md)
- [Network Communication](../../concepts/distributed-systems/patterns/network-communication.md)
- [Message Brokers (Kafka, RabbitMQ, SQS)](../distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [Kubernetes Basics](../../concepts/distributed-systems/kubernetes/kubernetes-basics.md)
- [Secrets Management](../../concepts/security/secrets/secrets-management.md)
- [System Design](../../concepts/backend/architecture/system-design.md)
- [Health, Liveness & Readiness Checks](../../concepts/backend/architecture/health-liveness-readiness.md)
- [Kong](../../concepts/backend/api-gateways/kong.md) · [NGINX](../../concepts/backend/api-gateways/nginx.md) · [Traefik](../../concepts/backend/api-gateways/traefik.md) · [AWS API Gateway](../../concepts/backend/api-gateways/aws-api-gateway.md) · [Spring Cloud Gateway](../../concepts/backend/api-gateways/spring-cloud-gateway.md)
- [Consul](../../concepts/backend/service-discovery/consul.md) · [Eureka](../../concepts/backend/service-discovery/eureka.md)
- [ELK/EFK Stack](../../concepts/backend/observability/elk-stack.md) · [Grafana Loki](../../concepts/backend/observability/grafana-loki.md) · [Prometheus](../../concepts/backend/observability/prometheus.md) · [Grafana](../../concepts/backend/observability/grafana.md) · [Jaeger](../../concepts/backend/observability/jaeger.md) · [Zipkin](../../concepts/backend/observability/zipkin.md) · [OpenTelemetry](../../concepts/backend/observability/opentelemetry.md)
- [Resilience4j](../../concepts/backend/resilience/resilience4j.md) · [Hystrix](../../concepts/backend/resilience/hystrix.md) · [Polly](../../concepts/backend/resilience/polly.md)
- [Spring Cloud Config](../../concepts/backend/data/spring-cloud-config.md)
