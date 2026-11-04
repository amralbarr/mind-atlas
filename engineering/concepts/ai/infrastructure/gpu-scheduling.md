# GPU-Aware Scheduling

Serving multiple AI models ([LLMs](../generation/llm.md), TTS, image/video generation) on a shared pool of GPUs is a resource-scheduling problem, not just a deployment problem — a GPU's VRAM is a hard, finite resource that can't be overcommitted the way CPU/RAM often can, so something has to actively decide which models get to occupy it at any given moment. A **GPU-aware scheduler** is the component that makes that decision, sitting between a [model router](../../backend/architecture/system-design.md) and the actual [runtime](../containers/docker.md) running each model.

## Why This Doesn't Reduce to Ordinary Autoscaling

Ordinary horizontal autoscaling assumes you can just start another replica when load increases. GPU-bound inference breaks that assumption in two ways:

- **VRAM is not fungible like RAM.** A 24GB video-generation model either fits in the free VRAM on a card or it doesn't — there's no graceful degradation, only an out-of-memory crash.
- **Loading a model is expensive.** Cold-starting a large model can take minutes (weights loaded from disk to GPU memory), unlike spinning up a stateless web server in seconds — so the scheduler must weigh eviction cost, not just current load.

## What the Scheduler Needs to Know

| Per-node (GPU) | Per-model |
|---|---|
| GPU model, total/used/free VRAM | Expected VRAM, peak VRAM |
| GPU utilization, temperature, power | Priority, [lifecycle mode](model-lifecycle-management.md) |
| Active GPU processes, GPU health | Preemptible? Exclusive GPU? |
| | Cold-start duration, active requests, queue depth, last-request time |

A scheduler that only tracks "how much VRAM is free right now" without the model-side data (priority, cold-start cost, preemptibility) can't make a good eviction decision — it can only tell you *that* something must be evicted, not *what*.

## GPU Telemetry

Never rely on parsing `nvidia-smi`'s human-readable text output as the scheduler's source of truth — it's meant for a human at a terminal, not a program, and its format isn't a stable contract across driver versions.

| Source | What it gives you |
|---|---|
| **NVML** (NVIDIA Management Library) | The C library `nvidia-smi` itself calls — programmatic, structured access to VRAM/utilization/temperature/power per GPU |
| **NVIDIA DCGM Exporter** | Exposes the same class of GPU metrics in [Prometheus](../../backend/observability/prometheus.md) format, for scraping alongside the rest of your [observability stack](../../../overviews/backend/microservices-tech-stack.md#observability-logs-metrics-traces) |
| **[NVIDIA GPU Operator](../../distributed-systems/kubernetes/nvidia-gpu-operator.md)** ([Kubernetes](../../distributed-systems/kubernetes/ingress.md)) | Automates installing drivers, the device plugin, and DCGM monitoring cluster-wide — see [Kubernetes Basics](../../distributed-systems/kubernetes/kubernetes-basics.md#kubernetes-ecosystem-for-mlgpu-workloads) |

Abstract this behind an interface (e.g. a `GpuProvider`) with a real implementation (`NvmlGpuProvider`) and a `MockGpuProvider` that returns simulated VRAM numbers — tests and local development should never require an actual NVIDIA GPU to be present.

## Safety Headroom

Never schedule a GPU to effectively 100% VRAM. Reserve a configurable minimum free VRAM (e.g. 3GB) as headroom — real usage always fluctuates slightly above the "expected" figure a model declares, and a model that OOMs mid-request is worse than one that was never scheduled.

## Preemption: Choosing What to Evict

When a request needs more VRAM than is currently free, the scheduler must pick eviction candidates from the running models. The naive approach — "evict whatever uses the most memory" — is wrong, because it ignores everything that makes eviction costly:

| Factor | Why it matters |
|---|---|
| Preemptible? | Some models (`always_on`) must never be evicted regardless of memory pressure |
| Active requests | Evicting a model mid-request drops in-flight work — see [Drain Before Stop](model-lifecycle-management.md#drain-before-stop) |
| Priority | A low-priority background model should be evicted before a high-priority one, even if it's not the largest |
| VRAM actually released | Evicting a small model that doesn't free enough VRAM just wastes the cold-start cost of stopping it |
| **Cold-start penalty** | A model that takes 4 minutes to reload is a far more expensive eviction than one that reloads in 8 seconds — track real cold-start time per model and weight eviction cost accordingly, not just current memory |
| Last-used time | All else equal, evict the model that's been idle longest |

**Exclusive GPU workloads** (a very large [LLM](../generation/llm.md), large video/image generation) need the opposite of preemption: before launching one, the scheduler must proactively drain and stop *other* workloads sharing that GPU, verify enough VRAM is actually free, then launch — and restore the prior baseline once the exclusive job completes.

## Distributed Coordination

Every lifecycle decision that touches a given GPU (starting a model, stopping a model, evicting for a new request) must be serialized — two requests racing to change the same GPU's state simultaneously is a correctness bug, not a performance one. Use a [distributed lock](../../distributed-systems/patterns/distributed-locks.md) scoped per-GPU (e.g. `lock:gpu:gpu-node-01:0`) around any state-changing operation.

## OOM as a Scheduler Failure, Not a Crash to Restart

A CUDA out-of-memory error means the scheduler's resource accounting was wrong somewhere — not just an ordinary crash to retry. Treat it as first-class scheduler feedback:

1. Record the telemetry at the moment of failure (node, workload, actual free VRAM).
2. Mark the attempt failed — don't blindly restart in a tight crash loop (see [Resilience Patterns](../../../overviews/backend/microservices-tech-stack.md#resilience-patterns) for the general retry/backoff/circuit-breaker reasoning this borrows from).
3. Apply a bounded retry with backoff, and consider an alternative node or a different eviction candidate before retrying on the same GPU.

## Common Questions

**Why not just let [Kubernetes](../../distributed-systems/kubernetes/ingress.md) handle GPU scheduling?**
> [Kubernetes](../../distributed-systems/kubernetes/ingress.md)' device plugin model treats a GPU largely as an indivisible unit to hand to one pod — it doesn't natively understand that multiple models with fractional, fluctuating VRAM needs might safely share one physical GPU, or that eviction cost differs wildly by model. [Kubernetes](../../distributed-systems/kubernetes/ingress.md) GPU Operator solves *driver/monitoring* infrastructure, not *this* scheduling problem — the priority/preemption/cold-start-aware logic above still has to be built, even after migrating orchestration to [Kubernetes](../../distributed-systems/kubernetes/ingress.md).

**Is this the same problem as ordinary CPU/RAM-based container scheduling?**
> Structurally similar (bin-packing with priorities and eviction), but VRAM's all-or-nothing failure mode (OOM crash, not graceful throttling) and the multi-minute cold-start cost for large models make eviction decisions far more consequential than reshuffling a stateless web container.

## Related

- [Model Lifecycle Management](model-lifecycle-management.md)
- [Distributed Locks](../../distributed-systems/patterns/distributed-locks.md)
- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Kubernetes Basics](../../distributed-systems/kubernetes/kubernetes-basics.md)
- [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md)
