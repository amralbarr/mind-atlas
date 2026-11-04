# Health, Liveness & Readiness Checks

"Is this process running?" and "can this process actually handle a request right now?" are different questions, and conflating them is a real source of production incidents — a process can be alive (not crashed) while genuinely unable to serve traffic (still initializing, still loading a large in-memory dataset or model, temporarily overloaded, mid-shutdown). Routing traffic based on process-alive alone sends requests to something that isn't ready for them.

## The Two (or Three) Checks

| Check | Question it answers | What acts on it |
|---|---|---|
| **Liveness** | "Is this process alive and not deadlocked/hung?" | The orchestrator ([Kubernetes](../../distributed-systems/kubernetes/ingress.md), a process manager like [PM2](../../../commands/pm2.md)) — a failing liveness check gets the process **restarted** |
| **Readiness** | "Can this instance handle a request *right now*?" | The load balancer / router — a failing readiness check gets the instance **removed from rotation**, not restarted |
| **Startup** (some platforms add this as a third, separate check) | "Has initial startup finished?" | Suppresses liveness checks during a slow boot, so a legitimately-still-starting process doesn't get killed for failing a liveness check it hasn't reached yet |

The critical distinction is the **action** each check triggers: a liveness failure says "kill and restart me," a readiness failure says "just don't send me traffic for now, I might recover" — using the wrong check for the wrong condition produces exactly the wrong response (e.g. restarting a process that was just temporarily busy, when removing it from rotation briefly would have been enough).

## A Concrete Failure Mode This Prevents

A service that loads a large model or dataset into memory at startup:

```text
process starts → HTTP server binds to port → begins loading 20GB model into memory
```

If "the port is open" is treated as "ready," a load balancer sends real traffic the instant the process starts — every one of those requests fails or times out until loading finishes minutes later. A separate `/ready` endpoint that only returns success once loading completes prevents this exactly: the process is alive (liveness passes) but not yet ready (readiness fails) for that window.

## Typical Implementation

```text
GET /health   → 200 if the process is alive and its event loop/main thread isn't hung
GET /ready    → 200 only if the process can actually serve a request right now
                (dependencies reachable, required data/model loaded, not mid-shutdown)
```

A readiness check often needs to verify more than the liveness check does — that a database connection is up, that a required model is loaded — while a liveness check should stay cheap and fast, since it's polled frequently and shouldn't itself become a performance problem.

## Related to Graceful Shutdown

Readiness also covers the *shutdown* side of the same problem: when a process is draining in-flight requests before stopping (see [Model Lifecycle Management § Drain Before Stop](../../ai/infrastructure/model-lifecycle-management.md#drain-before-stop) for a concrete state-machine treatment of this), it should fail its readiness check immediately — signaling "stop sending me new work" — while continuing to pass liveness until the drain finishes, since it's still alive and correctly finishing existing work.

## Common Questions

**Doesn't [Kubernetes](../../distributed-systems/kubernetes/ingress.md) just call these "probes"?**
> Yes — `livenessProbe`, `readinessProbe`, and `startupProbe` are [Kubernetes](../../distributed-systems/kubernetes/ingress.md)' names for exactly this pattern (see [Kubernetes Basics](../../distributed-systems/kubernetes/kubernetes-basics.md)). The underlying concept isn't [Kubernetes](../../distributed-systems/kubernetes/ingress.md)-specific, though — any load balancer or orchestrator that routes traffic to a pool of instances needs the same liveness/readiness distinction, whether or not it uses that exact vocabulary.

**Can a single `/health` endpoint serve both purposes?**
> Technically yes if it's kept simple, but it's a common source of bugs once the checks' *actions* diverge — a heavier `/health` check that also verifies a downstream dependency, used as a liveness probe, can cause an orchestrator to restart a perfectly-alive process just because a downstream dependency hiccuped. Separating the endpoints makes each check's failure mode (restart vs. remove-from-rotation) match what's actually wrong.

## Related

- [Model Lifecycle Management](../../ai/infrastructure/model-lifecycle-management.md)
- [Kubernetes Basics](../../distributed-systems/kubernetes/kubernetes-basics.md)
- [HTTP Status Codes](../api/http-status-codes.md)
- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Load Balancing](../../networking/load-balancing.md)
- [PM2 Commands](../../../commands/pm2.md)
