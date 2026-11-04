# Model Lifecycle Management

When serving several AI models on a shared, VRAM-constrained pool of GPUs, not every model should behave the same way. A small classifier and a 24GB video-generation model have completely different cost profiles for sitting idle versus being loaded on demand — **lifecycle management** is the set of rules for when a model should be running, stopped, or somewhere in between, and how it transitions between those states safely. This is the model-serving counterpart to [GPU-Aware Scheduling](gpu-scheduling.md), which decides *which* model to evict; this note covers *how* a model's own state changes over time.

## Lifecycle Modes

| Mode | Default state | Behavior |
|---|---|---|
| **`always_on`** | Running | High priority, never automatically preempted, automatically restarted if it crashes — reserved for models the system can't function without (e.g. a core production [LLM](../generation/llm.md)) |
| **`warm`** | Running | Normally kept running for low latency, but *can* be stopped if a higher-priority workload needs the VRAM — restored afterward |
| **`on_demand`** | Stopped | Starts only when a request arrives, stays warm for an idle timeout after the last request, then stops again — the model-serving equivalent of scale-to-zero |
| **`batch`** | Stopped | For expensive workloads (video generation, bulk [embeddings](../ingestion/embeddings.md)): load the model once, drain the whole queue while it's warm, then stop after a cooldown once the queue is empty — avoids paying the cold-start cost per job |

## The `on_demand` Request Flow

```text
request → scheduler → reserve GPU resources → start model
  → wait for readiness → process request
  → remain warm for idle timeout → stop
```

The "remain warm for idle timeout" step matters: without it, a burst of several requests seconds apart would each pay the full cold-start cost, when one warm-up would have served all of them.

## Model State Machine

A model's process being alive is not the same thing as the model being ready to serve — a Python process can be running seconds before a 20GB model has actually finished loading into GPU memory. Model that distinction explicitly as a state machine rather than a boolean:

```text
STOPPED → STARTING → LOADING → READY → BUSY
                                  ↓
                              DRAINING → STOPPING → STOPPED
                                  
(any state) → ERROR
```

| State | Meaning |
|---|---|
| `STOPPED` | No process running |
| `STARTING` | Process launched, not yet loading the model |
| `LOADING` | Process alive, model weights being loaded — **not yet able to serve** |
| `READY` | Model loaded, able to accept requests |
| `BUSY` | Actively serving a request |
| `DRAINING` | No longer accepting new requests, finishing in-flight ones |
| `STOPPING` | Shutting down |
| `ERROR` | Failed to start/load, or crashed |

Expose `/health` (is the process alive) and `/ready` (can it actually serve inference right now) as separate signals — see [Health, Liveness & Readiness Checks](../../backend/architecture/health-liveness-readiness.md) for why conflating the two causes real production bugs (traffic routed to a process that's alive but still loading a model).

## Drain Before Stop

Never kill a model process that's actively serving requests. Before stopping a model (whether for routine idle-timeout or for GPU preemption), transition it through `DRAINING`: stop accepting new requests, wait for the active-request count to hit zero (up to a configurable maximum drain timeout), and only then proceed to `STOPPING`. This is the same graceful-shutdown reasoning behind connection draining in a load balancer or a rolling [Kubernetes](../../distributed-systems/kubernetes/ingress.md) deployment — applied here to GPU memory instead of a network connection.

## Cold Start Is Not Free — Track It

Two models with similar VRAM footprints can have wildly different cold-start costs:

```text
Model A: 6 GB VRAM, 8-second cold start
Model B: 12 GB VRAM, 240-second cold start
```

A scheduler that doesn't track this will treat both as equally cheap to evict — in reality, evicting Model B is a much bigger bet that the eviction was worth it, since a request arriving moments later pays a 4-minute penalty. Record real process-start time, model-load time, readiness time, and first-inference time per model, and feed the observed cold-start duration back into eviction decisions (see [GPU-Aware Scheduling § Preemption](gpu-scheduling.md#preemption-choosing-what-to-evict)).

## Baseline Restoration

After a preemption or a batch job completes, don't blindly restart everything that was stopped — restore according to each model's own lifecycle policy:

| Mode | After being stopped |
|---|---|
| `always_on` | Restore |
| `warm` | Restore |
| `on_demand` | Leave stopped — it'll start again on the next request |
| `batch` | Leave stopped — it'll start again when its queue has work |

Track *why* a model is stopped (intentionally preempted vs. its own idle-timeout vs. a crash) — a model that was preempted should come back once resources free up; a model that's stopped because nobody's requested it shouldn't be force-restarted just because a GPU has spare capacity again.

## Common Questions

**Isn't this just "scale to zero," the way serverless platforms already do it?**
> The core idea (stop when idle, start on demand) is the same, but the cost asymmetry is much larger — a serverless function typically cold-starts in milliseconds to low seconds; a multi-gigabyte model can take minutes. That gap is why lifecycle modes beyond plain on-demand (`warm`, `batch`) exist here: the cold-start cost is high enough that avoiding it, when justified by request patterns, is worth the idle GPU memory it costs.

**Why track four separate readiness modes instead of just "running or not"?**
> Because "running" (`STARTING`/`LOADING`) and "ready to serve" (`READY`) are genuinely different states with different implications for a router — sending a request to a `LOADING` model either queues unnecessarily or fails outright, depending on how the runtime handles it. Modeling the states explicitly makes each transition (and its edge cases — a model stuck in `LOADING`, a startup timeout) something the scheduler can reason about and test deterministically.

## Related

- [GPU-Aware Scheduling](gpu-scheduling.md)
- [Health, Liveness & Readiness Checks](../../backend/architecture/health-liveness-readiness.md)
- [Message Queues](../../distributed-systems/messaging/queues.md)
- [Resilience Patterns](../../../overviews/backend/microservices-tech-stack.md#resilience-patterns)
- [systemctl (systemd) Commands § Running a Docker Container as a systemd Service](../../../commands/systemctl.md#running-a-docker-container-as-a-systemd-service) — why a slow-loading model needs a generous `TimeoutStartSec` when the container is systemd-supervised
