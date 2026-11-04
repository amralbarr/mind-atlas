# Monolith vs Microservices

This is one of the most important backend/[system design](system-design.md) decisions, especially for [Node.js](https://nodejs.org/) and [NestJS](https://nestjs.com/) engineers working with distributed systems and scalable architectures.

## What Is a Monolith?

> A single unified application where all features exist in one codebase and are deployed together.

Example structure:

```text
App
 ├── Auth
 ├── Users
 ├── Payments
 ├── Orders
 ├── Notifications
 └── Database
```

Everything runs as ONE application.

Example deployment:

```text
Single Server
     ↓
Single Application
```

### Monolith Characteristics

- one codebase
- one deployment
- shared database
- tightly connected modules

### Advantages of Monolith

1. **Simple to start** — very easy for MVPs, startups, and small teams.
2. **Easier debugging** — everything is in one place.
3. **Faster initial development** — no distributed-system complexity.
4. **Simpler deployment** — deploy one app only.
5. **Lower infrastructure complexity** — no service discovery, message brokers, or orchestration needed.

### Disadvantages of Monolith

1. **Scaling problems** — you must scale the entire application even if only one feature is busy.
2. **Tight coupling** — modules become highly dependent on each other.
3. **Large codebase** — over time it can become a "Big Ball of Mud."
4. **Slower deployments** — a small change requires a full redeployment.
5. **Harder team scalability** — large teams conflict frequently in a shared codebase.

## What Are Microservices?

> Splitting an application into small independent services that communicate over the network.

Example:

```text
Auth Service
Users Service
Orders Service
Payments Service
Notification Service
```

Each service is independent, deployable separately, and owns its own logic.

Example architecture:

```text
Client
  ↓
API Gateway
  ↓
 ├── Auth Service
 ├── User Service
 ├── Order Service
 └── Payment Service
```

### Characteristics of Microservices

- distributed system
- separate deployments
- service isolation
- [network communication](../../distributed-systems/patterns/network-communication.md)
- decentralized ownership

### Advantages of Microservices

1. **Independent scaling** — scale only the busy services (e.g. scale just the Payments service under heavy load).
2. **Independent deployments** — deploy a service without affecting others.
3. **Better team scalability** — teams own services independently.
4. **Technology flexibility** — different services can use Node.js, Python, Go, Java, etc.
5. **Fault isolation** — one service failure doesn't necessarily crash everything.

### Disadvantages of Microservices

1. **Much more complex** — distributed systems are hard.
2. **[Network communication](../../distributed-systems/patterns/network-communication.md) overhead** — services communicate over [HTTP](../../networking/http.md), [gRPC](../api/grpc.md), or message brokers.
3. **Data consistency problems** — [distributed transactions](../../databases/distributed/distributed-transactions.md) become difficult.
4. **Harder debugging** — requires tracing, centralized logging, and observability.
5. **Infrastructure complexity** — needs [Docker](../../containers/docker.md), [Kubernetes](../../distributed-systems/kubernetes/ingress.md), service discovery, monitoring, and gateways.

## Database Architecture Difference

**Monolith:** usually one shared database.

**Microservices:** usually a [database per service](database-per-service.md). This is a very important concept.

## Communication Between Services

| Method | Example |
| --- | --- |
| [HTTP](../../networking/http.md) [REST](../api/rest.md) | API calls |
| [gRPC](../api/grpc.md) | high-performance RPC |
| Message Broker | [RabbitMQ](../../distributed-systems/messaging/rabbitmq.md), [Kafka](../../distributed-systems/messaging/kafka.md) |
| Event Streaming | [Kafka](../../distributed-systems/messaging/kafka.md) streams |

### Synchronous vs Asynchronous

**Sync communication** — Service A waits for a response (e.g. [REST](../api/rest.md), [gRPC](../api/grpc.md)).

**Async communication** — message/event driven (e.g. [Kafka](../../distributed-systems/messaging/kafka.md), [RabbitMQ](../../distributed-systems/messaging/rabbitmq.md)). Very important for scalability.

## Scaling Comparison

**Monolith scaling (horizontal):** duplicate the full application. Problem: even unused modules scale too.

**Microservices scaling:** scale only the required services — much more efficient.

## Deployment Difference

| Monolith | Microservices |
| --- | --- |
| Single deployment | Multiple deployments |
| Easier [CI/CD](../../devops/ci-cd.md) | Complex [CI/CD](../../devops/ci-cd.md) |
| Simple rollback | Service-specific rollback |

## Common Real Architecture Evolution

Most companies follow this path:

```text
Start Monolith
     ↓
Scale
     ↓
Extract Microservices gradually
```

## Modular Monolith

A modern best practice.

**What is it?** A monolith with strict modular boundaries, clean architecture, and feature separation.

```text
Modules:
 ├── Auth
 ├── Users
 ├── Payments
```

but still a single deployment. Very popular today.

**Why it's powerful:** you get the simplicity of a monolith with a cleaner scalability path, without distributed complexity.

## CAP Theorem

Microservices discussions often bring up the **CAP theorem** — an advanced [system design](system-design.md) topic. Distributed systems can only guarantee 2 of:

- Consistency
- Availability
- Partition tolerance

## Event-Driven Architecture

Very common with microservices. Example: an `OrderCreated` event, where other services react asynchronously.

## API Gateway

A common microservices component. Handles routing, auth, [rate limiting](rate-limiting.md), and aggregation.

## Service Discovery

Needed in dynamic systems. Examples: [Consul](../service-discovery/consul.md), [Eureka](../service-discovery/eureka.md), [Kubernetes](../../distributed-systems/kubernetes/ingress.md) [DNS](../../networking/dns.md).

## Observability

Microservices REQUIRE centralized logging, metrics, and tracing. Tools: [Prometheus](../observability/prometheus.md), [Grafana](../observability/grafana.md), [Jaeger](../observability/jaeger.md), [ELK stack](../observability/elk-stack.md).

See [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md) for the full breakdown of each of these — concrete tool comparisons, resilience patterns (circuit breakers, retries), and configuration/secrets management.

## Comparison Table

| Feature | Monolith | Microservices |
| --- | --- | --- |
| Complexity | Low | High |
| Deployment | Single | Distributed |
| Scaling | Whole app | Per service |
| Team Scalability | Limited | Excellent |
| Fault Isolation | Weak | Strong |
| Infrastructure | Simple | Complex |
| Development Speed | Faster initially | Slower initially |
| Debugging | Easier | Harder |

## Common Questions

**When should you use a monolith?**

> For startups, MVPs, smaller teams, or systems without large-scale distributed requirements, because monoliths are simpler to develop, deploy, and maintain initially.

**When should you use microservices?**

> When systems require independent scaling, autonomous teams, high scalability, fault isolation, or heterogeneous technology stacks.

**Biggest challenge in microservices?**

- [distributed transactions](../../databases/distributed/distributed-transactions.md)
- observability
- network failures
- [eventual consistency](../../distributed-systems/patterns/eventual-consistency.md)

### Senior-Level Answer

> Monolithic architecture centralizes all application functionality into a single deployable unit, offering simplicity and faster development initially. Microservices decompose systems into independently deployable services, enabling scalability, fault isolation, and autonomous team ownership at the cost of increased distributed system complexity.

### Best Practice Recommendation

For most modern systems:

```text
Start with modular monolith
Scale to microservices only when necessary
```

This is considered mature architecture thinking.

### Easy Way to Remember

```text
Monolith = one big application
Microservices = many small services
```

## Related

- [ORM](../data/orm.md)
- [Distributed Databases](../../databases/distributed/distributed-databases.md)
- [NestJS Overview](../nestjs/nestjs-overview.md)
- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
