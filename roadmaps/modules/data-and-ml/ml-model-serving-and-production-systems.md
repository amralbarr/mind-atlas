# Module: ML Model Serving & Production Systems

**Category:** Data & ML · **Typical duration:** 3–4 weeks (15–20 hrs/week) · **Prerequisite modules:** [Deep Learning Foundations](deep-learning-foundations.md), [Containers & CI/CD](../backend/containers-and-ci-cd.md), [Databases & Caching](../backend/databases-and-caching.md)

## Goal

Take a trained model from a notebook to a production system that serves predictions reliably, at scale, and without silently going stale.

## Core topics

- [ ] Serving patterns: batch vs online/real-time inference, synchronous API vs async queue-based scoring
- [ ] Wrapping a model behind an API with input validation and versioned endpoints
- [ ] Feature stores: why one exists, online/offline consistency, point-in-time correctness (avoiding training/serving skew)
- [ ] Model packaging and a model registry: versioning, rollback, reproducibility
- [ ] Rollout strategies for a new model version: shadow deployment, canary, champion/challenger
- [ ] Latency/throughput tradeoffs for classical ML vs deep learning models; batching requests
- [ ] Basic load testing of a serving endpoint

## Resources

- A model-serving framework's official docs (e.g. a dedicated model server, or your API framework plus a model-serving library)
- A feature-store project's own docs for the online/offline-consistency concept, even if you don't deploy one in full

## Milestone deliverable

Serve one of your earlier milestone models behind a versioned API endpoint, with a canary or shadow rollout path for a second model version and a basic load test report.

## Related concepts

[Staged Rollout](../../../engineering/concepts/backend/delivery/staged-rollout.md), [KServe](../../../engineering/concepts/distributed-systems/kubernetes/kserve.md), [Kubernetes Basics](../../../engineering/concepts/distributed-systems/kubernetes/kubernetes-basics.md)
