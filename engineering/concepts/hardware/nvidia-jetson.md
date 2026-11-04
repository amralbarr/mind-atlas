# NVIDIA Jetson

NVIDIA Jetson is a family of embedded edge-AI compute modules — small boards that pack an ARM CPU and an NVIDIA GPU into a low-power form factor, running the same CUDA/TensorRT/JetPack software stack used on NVIDIA's data-center GPUs. It's the step up from a Raspberry Pi-class board (see [Raspberry Pi AI HAT+](raspberry-pi-ai-hat.md)) when a project needs real GPU-class throughput at the edge — multiple camera/sensor streams, heavier models, or production-grade latency and frame rate.

## The Orin lineup

| Module | Peak AI performance | Power | Typical fit |
|---|---|---|---|
| Jetson Orin Nano (Super/2) | ~67–78 TOPS (INT8, sparse) | 7–25 W | Entry-level robotics/edge AI — drones, single-robot vision, cost-sensitive deployments |
| Jetson AGX Orin 32GB | Up to 200 TOPS | 15–40 W | Mid-tier production edge inference |
| Jetson AGX Orin 64GB | Up to 275 TOPS | 15–60 W | Heaviest edge workloads — multiple camera/sensor streams, larger models, tightest latency budgets |

(The newer Blackwell-generation **Jetson Thor** modules push considerably further, up into the thousands of FP4 TFLOPS, for the most demanding robotics/autonomy workloads.)

## Why it matters for a multi-sensor pipeline

A pipeline that runs detection + pose + tracking on camera frames *and* [radar point-cloud tracking](../hardware/radar-point-cloud.md) *and* [sensor fusion](../robotics/sensor-fusion.md)/event logic, across multiple cameras, is a meaningfully heavier compute load than a single-camera object detector. Jetson's advantage over a Raspberry Pi + NPU setup in that scenario is:

- **A full CUDA/TensorRT ecosystem** — broader framework support (PyTorch, ONNX Runtime, DeepStream for multi-stream video pipelines) rather than a narrower accelerator-specific toolchain.
- **Headroom for multiple concurrent models and streams** on one device, rather than one NPU budget shared across every task.
- **A well-trodden path from prototype to production** — the same JetStream/JetPack stack scales from a Nano-class dev board up to an AGX Orin for the deployed system, without redesigning the software.

The tradeoff is cost and power relative to a Raspberry Pi-class device — which is why the common approach is to prototype on a laptop/GPU workstation, move to a Raspberry Pi + AI accelerator for a lightweight edge test, and only reach for a Jetson once the target deployment's throughput or multi-stream requirements actually demand it.

## Related

- [Raspberry Pi AI HAT+](raspberry-pi-ai-hat.md)
- [Sensor Fusion](../robotics/sensor-fusion.md)
- [Radar Point Cloud](radar-point-cloud.md)
