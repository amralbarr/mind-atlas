# Mesh Architecture

**Mesh architecture** is a design where multiple services (or nodes) communicate directly with each other over a network, instead of going through a single central hub.

## Core Idea

Instead of:

```text
Client → Central Service → Other Services
```

you have:

```text
Service A ↔ Service B ↔ Service C ↔ Service D
```

Every service can talk to others, forming a mesh network.

## Types of Mesh

### Full Mesh

Every service connects to every other service:

```text
A ↔ B ↔ C ↔ D (all interconnected)
```

Very reliable, but hard to scale — the number of connections grows quickly.

### Partial Mesh

Services connect only to the peers they actually need. This is more practical for real systems.

## Service Mesh (Modern Meaning)

Today, "mesh architecture" often refers specifically to a **service mesh** — a dedicated infrastructure layer that manages communication between services. Popular implementations include Istio and Linkerd.

### How a Service Mesh Works

Instead of putting networking logic inside application code, a **sidecar proxy** is attached to each service:

```text
Service A → Proxy A → Proxy B → Service B
```

The mesh layer handles:

- Routing
- [Load balancing](../../networking/load-balancing.md)
- Security (mTLS)
- Monitoring and observability

## Why Use Mesh Architecture?

### Advantages

- No single point of failure.
- High flexibility.
- Better service-to-service communication.
- Built-in observability (logs, metrics, tracing).
- Security enforced between services.

### Challenges

- Complex to operate.
- Harder to debug.
- Network overhead from the extra proxy hop.
- Connection count grows quickly in large systems.

## Mesh vs. Other Architectures

| Architecture | Structure | Example |
|---|---|---|
| Monolith | One system | Single app |
| Client-server | Central server | Web apps |
| Fan-out | One → many | Events |
| Mesh | Many ↔ many | Microservices |

## Example

Without a mesh, a request might flow linearly:

```text
Frontend → API → Worker → DB
```

With a mesh, services can call each other directly as needed:

```text
Frontend ↔ API ↔ Worker ↔ OCR Service ↔ DB Service
```

Services can call each other directly, share data faster, and react dynamically without every request passing through one central point.

## When to Use Mesh

Use mesh architecture when:

- The system has many microservices.
- Communication needs to be flexible, not fixed to one hub.
- Advanced networking features (mTLS, tracing, fine-grained routing) are needed.

## One-Line Definition

> Mesh architecture is a network where services communicate directly with each other in a decentralized way.

## Related

- [Single-Threading](single-threading.md)
- [Kubernetes Basics](../kubernetes/kubernetes-basics.md)
- [Monolith vs Microservices](../../backend/architecture/monolith-vs-microservices.md)
- [System Design](../../backend/architecture/system-design.md)
- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
