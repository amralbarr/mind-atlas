# Module: LLM Deployment & Inference

**Category:** AI / [LLM](../../../engineering/concepts/ai/generation/llm.md) · **Typical duration:** 5–6 weeks (15–20 hrs/week) · **Prerequisite modules:** [Deep Learning Foundations](../data-and-ml/deep-learning-foundations.md), [Containers & CI/CD](../backend/containers-and-ci-cd.md)

## Goal

Serve an open-weight LLM on real hardware, fast and cheaply — valuable wherever on-prem, in-country, or cost-controlled hosting matters more than calling a managed API.

## Core topics

- [ ] GPU memory math: parameters × bytes-per-parameter plus KV cache; why large models need multiple GPUs
- [ ] Prefill vs decode, time-to-first-token, tokens/sec, latency vs throughput
- [ ] Continuous batching, paged-attention-style memory management, speculative decoding, prefix caching
- [ ] A production inference server: tensor parallelism, max context length, GPU memory utilization, load testing
- [ ] Quantization formats and their quality/speed/memory tradeoffs
- [ ] A comparison of at least two serving engines on speed, features, and ease of operation
- [ ] Serving at scale: GPU-aware orchestration, autoscaling on queue depth/utilization, model routing between a small and large model

## Resources

- Your chosen inference engine's official docs and benchmark scripts
- A load-testing tool's quickstart for benchmarking throughput/latency

## Milestone deliverable

A benchmark report comparing a model's full-precision vs quantized variants on at least one serving engine (latency, throughput, memory, and quality against your [evaluation suite](llm-evaluation-and-guardrails.md)), followed by switching your portfolio project to the self-hosted model.

## Related concepts

[Fine-tuning](../../../engineering/concepts/ai/infrastructure/fine-tuning.md), [LoRA](../../../engineering/concepts/ai/infrastructure/lora.md), [GPU Scheduling](../../../engineering/concepts/ai/infrastructure/gpu-scheduling.md), [Model Lifecycle Management](../../../engineering/concepts/ai/infrastructure/model-lifecycle-management.md)
