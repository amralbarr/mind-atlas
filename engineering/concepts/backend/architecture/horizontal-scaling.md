# Horizontal Scaling (Scaling Out)

Horizontal scaling is handling more simultaneous load by running **more copies** of an application — more containers, more server instances — behind something that distributes traffic across them, rather than making one instance bigger. It's the application-layer counterpart to the database-layer scaling ladder ([connection pooling](../../databases/relational/connection-pooling.md) → [read replicas](../../databases/relational/read-replicas.md) → [partitioning](../../databases/relational/partitioning.md) → [sharding](../../databases/distributed/sharding.md) — see [Database Scaling Strategies](../../../overviews/databases/database-scaling-strategies.md)): both start from "one instance is the bottleneck" and solve it by adding more, rather than making the one instance bigger.

## Horizontal vs. Vertical Scaling

| | Vertical scaling (scale up) | Horizontal scaling (scale out) |
|---|---|---|
| How capacity grows | A bigger machine — more CPU, RAM, faster disk, on the *same* instance | More machines/containers running the *same* instance, in parallel |
| Ceiling | Hard — there's a biggest machine money can buy, and it eventually becomes the single point of failure too | Much higher in practice — add another container/instance as long as the pool behind the load balancer can grow |
| Downtime to scale | Often requires a restart or even a migration to new hardware | Usually zero — a new instance joins the pool and starts taking traffic without touching existing ones |
| Failure blast radius | One machine going down takes the whole service down | One instance going down still leaves the others serving traffic |
| Complexity added | None — the application doesn't need to change at all | Requires the application to be stateless (or externalize state) and requires a way to distribute traffic — see below |
| Cost curve | Non-linear — doubling a single machine's specs often costs far more than double | Roughly linear — twice the instances costs roughly twice as much |

Vertical scaling is simpler and is usually the first lever reached for because it requires zero application changes, but it hits a real ceiling (both technical — the biggest instance size a cloud provider offers — and financial, since high-end hardware scales in cost faster than in capacity) and never addresses the single-point-of-failure problem. Horizontal scaling is adopted once that ceiling is reached, or once availability itself (not just raw capacity) is a requirement.

## Why Containers Made This the Default

Before containers, "add another instance" meant provisioning another physical or virtual machine — a slow, heavyweight operation. [Docker](../../containers/docker.md) (and [OCI](../../containers/oci.md)-compliant containers generally) package an application and its dependencies into a portable image that can be started as a new, isolated instance in seconds, on any host running a compatible container runtime. This is what makes horizontal scaling practical at the pace modern traffic actually demands — spinning up five more containers to absorb a traffic spike takes seconds, not the minutes-to-hours a new VM provisioning cycle would take.

```text
Low traffic:                    Traffic spike:

Client → LB → [Container 1]     Client → LB → [Container 1]
                                              → [Container 2]
                                              → [Container 3]
                                              → [Container 4]
```

In a container orchestrator like [Kubernetes](../../distributed-systems/kubernetes/kubernetes-basics.md), this is usually automated: a Horizontal Pod Autoscaler watches a metric (CPU, memory, request rate, or a custom metric via something like [KEDA](../../distributed-systems/kubernetes/keda.md)) and adjusts the replica count up or down within configured bounds, without a human manually deciding when to add or remove instances.

## The Prerequisite: Statelessness

Horizontal scaling only works cleanly if any instance can handle any request — which means instances can't hold request-specific state that only *they* know about. A user's session stored in one container's local memory becomes invisible the moment the [load balancer](../../networking/load-balancing.md) routes that user's next request to a *different* container. The fix is externalizing state the application needs to share across instances — sessions in Redis, uploaded files in [object storage](../../cloud/infrastructure/object-storage.md) rather than local disk, and the actual source-of-truth data in a shared database — so every container is interchangeable and disposable. This is the same reasoning [Load Balancing](../../networking/load-balancing.md)'s "sticky sessions" section describes as a workaround rather than a fix: sticky sessions exist specifically to paper over state an application should have externalized instead.

## Distributing Traffic Across Instances

Adding more containers only helps if something routes incoming requests across all of them — this is the job of a [load balancer](../../networking/load-balancing.md) (or a [reverse proxy](../../networking/reverse-proxy.md)/[API gateway](../api-gateways/kong.md) acting as one), using an algorithm like round robin or least connections to spread requests. Each instance should also expose a health check so the load balancer stops routing to one that's failed or still starting up — see [Health, Liveness & Readiness](health-liveness-readiness.md).

## Horizontal Scaling at the Database Layer

The same "more instances instead of a bigger instance" idea applies to databases too, but it's a harder problem because a database holds state — unlike a stateless application container, you can't just duplicate a database node and expect it to behave like one logical database without doing real work to keep the copies consistent or to decide which copy owns which data. See [Database Scaling Strategies](../../../overviews/databases/database-scaling-strategies.md) for how that ladder (pooling → [read replicas](../../databases/relational/read-replicas.md) → [partitioning](../../databases/relational/partitioning.md) → [sharding](../../databases/distributed/sharding.md)) plays out, and [Distributed Databases](../../databases/distributed/distributed-databases.md) for the general theory of horizontally scaled, multi-node databases.

## Common Questions

**Does horizontal scaling remove the need for vertical scaling entirely?**
> No — the two combine in practice. Each individual container still has a CPU/memory size (vertical scaling happens there), and the *number* of those containers is what scales horizontally. Picking a reasonable per-instance size and then scaling the instance count is usually more cost-effective than a few giant instances.

**What stops horizontal scaling from being infinite?**
> In practice: the database or other shared backing store becomes the bottleneck long before the application layer does, since the application containers are stateless and trivially replicated but the data they all read/write usually isn't (until it's deliberately scaled too — see [Database Scaling Strategies](../../../overviews/databases/database-scaling-strategies.md)). Cost and the load balancer's own capacity are secondary limits.

**Is horizontal scaling only relevant to web APIs?**
> No — it applies to any stateless workload: background workers consuming from a [queue](../../distributed-systems/messaging/queues.md), scheduled jobs, [gRPC](../api/grpc.md) services. Anything that can accept "more of the same thing running in parallel, each handling a subset of the work" benefits from the same pattern.

## Related

- [Load Balancing](../../networking/load-balancing.md) — the mechanism that actually distributes traffic across the scaled-out instances
- [Docker](../../containers/docker.md) — the container runtime that makes spinning up new instances fast enough for this to be practical
- [Kubernetes Basics](../../distributed-systems/kubernetes/kubernetes-basics.md) — the orchestrator that commonly automates adding/removing instances via autoscaling
- [KEDA](../../distributed-systems/kubernetes/keda.md) — event-driven autoscaling that can trigger horizontal scaling off custom metrics, not just CPU/memory
- [Health, Liveness & Readiness](health-liveness-readiness.md) — how a load balancer/orchestrator knows a newly scaled instance is actually ready for traffic
- [System Design](system-design.md) — lists horizontal scaling as one of the recurring building blocks of a scalable architecture
- [Database Scaling Strategies](../../../overviews/databases/database-scaling-strategies.md) — the equivalent scaling ladder on the data layer, which is harder precisely because data (unlike a stateless container) can't just be duplicated for free
- [Caching Strategies](caching-strategies.md) — a complementary lever that reduces how much load reaches the scaled-out instances in the first place
