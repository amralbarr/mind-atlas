# Raspberry Pi AI HAT+

The Raspberry Pi AI HAT+ is an add-on board for the Raspberry Pi 5 that adds a dedicated **Hailo neural-processing unit (NPU)**, letting the Pi run object detection, [pose estimation](../../overviews/ai/computer-vision/pose-estimation.md), and segmentation models directly on-device instead of on the Pi's own (comparatively weak) CPU/GPU. It's the practical way to turn a Raspberry Pi 5 into a real-time edge-AI vision device rather than a bottlenecked one.

## Variants

| Board | NPU | Performance | Notes |
|---|---|---|---|
| AI HAT+ (13 TOPS) | Hailo-8L | 13 TOPS | Entry-level; moderate vision workloads |
| AI HAT+ (26 TOPS) | Hailo-8 | 26 TOPS | Roughly 2× the Hailo-8L's resources; larger networks, multiple parallel models |
| AI HAT+ 2 (40 TOPS) | Hailo-10H | 40 TOPS, 8 GB dedicated on-board RAM | A newer chip architecture combining classic vision inference with generative-AI ([LLM](../ai/generation/llm.md)/VLM) capability locally |

TOPS (tera-operations per second) is the standard rough throughput figure for NPU/accelerator inference performance — higher isn't strictly "better" in isolation, it's about whether the target model(s) fit the budget at the frame rate needed.

## What it's for

Object detection, [pose estimation](../../overviews/ai/computer-vision/pose-estimation.md), and segmentation models ([YOLO](../ai/computer-vision/yolo.md) and similar) are compute-heavy per frame. Running them on a Raspberry Pi's CPU alone caps out at a few frames per second at best for any non-trivial model — usable for prototyping, not for a real-time pipeline. The AI HAT+'s Hailo NPU offloads that inference workload, freeing the Pi's CPU for the rest of the application (video capture, [sensor fusion](../robotics/sensor-fusion.md), event logic, API/dashboard serving) while the NPU handles the model forward pass.

## When it's the right choice vs. NVIDIA Jetson

| | Raspberry Pi 5 + AI HAT+ | [NVIDIA Jetson](nvidia-jetson.md) |
|---|---|---|
| Cost | Low | Higher |
| Ecosystem | Simpler, Pi-centric | Full CUDA/TensorRT stack, more ML framework support |
| Best for | Single camera/sensor, one or two models, cost-sensitive edge deployment | Multiple cameras/sensors, heavier models, production-grade throughput |
| Local generative AI ([LLM](../ai/generation/llm.md)/VLM) | Only the AI HAT+ 2 (Hailo-10H), and only lightweight models | Broad support across the Jetson lineup |

A common development path (seen in radar+camera fusion projects, for instance) is: develop and validate the pipeline on a laptop/GPU workstation first, then move the same pipeline to a Raspberry Pi 5 + AI HAT+ for an edge prototype, and only escalate to a Jetson if the Pi's throughput proves insufficient for the production target.

## Related

- [NVIDIA Jetson](nvidia-jetson.md)
- [YOLO](../ai/computer-vision/yolo.md)
- [Sensor Fusion](../robotics/sensor-fusion.md)
