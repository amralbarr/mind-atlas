# Module: MLOps & Cloud AI Platforms

**Category:** Platform · **Typical duration:** 3–4 weeks (15–20 hrs/week) · **Prerequisite modules:** [Containers & CI/CD](../backend/containers-and-ci-cd.md); pairs well with [LLM Deployment & Inference](../ai-llm/llm-deployment-and-inference.md)

## Goal

Ship and operate AI systems repeatably: versioned, tested, and deployable with one pipeline — and know what a target cloud's managed AI platform already does for you.

## Core topics

- [ ] Container orchestration basics: deployments, services, [ingress](../../../engineering/concepts/distributed-systems/kubernetes/ingress.md), config/secrets, autoscaling, health probes
- [ ] Experiment tracking and a model registry
- [ ] Prompt/dataset versioning and continuous evaluation as part of deployment
- [ ] [CI/CD](../../../engineering/concepts/devops/ci-cd.md) for ML: test → eval → build → deploy, with a progressive rollout strategy (canary/blue-green)
- [ ] [Infrastructure as code](../../../engineering/concepts/cloud/iac/infrastructure-as-code.md) basics for the resources your system needs
- [ ] One major cloud's managed AI stack end to end (pick the one your target employer/market actually uses): managed model hosting, a managed vector/search service, document-intelligence tooling, data-residency options

## Resources

- A container-orchestration platform's own tutorials, practiced locally first on a single-node setup
- An MLOps-focused free course covering experiment tracking, registries, and CI/CD for ML
- The chosen cloud provider's own AI-platform getting-started docs

## Milestone deliverable

Deploy your portfolio project's full stack (API, model serving, data store, observability) to a container orchestrator with [Helm](../../../engineering/concepts/distributed-systems/kubernetes/helm.md)-style packaging, with a CI pipeline that runs tests/evals on every PR and does a canary rollout.

## Related concepts

[Kubernetes Basics](../../../engineering/concepts/distributed-systems/kubernetes/kubernetes-basics.md), Helm, Infrastructure as Code, [Azure AI Foundry](../../../engineering/concepts/cloud/azure/azure-ai-foundry.md)
