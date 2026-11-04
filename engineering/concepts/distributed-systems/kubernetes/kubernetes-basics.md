# Kubernetes Basics

**[Kubernetes](ingress.md) (K8s)** is an open-source system for automating the deployment, scaling, and management of containerized applications. It was originally developed by Google and is now maintained by the Cloud Native Computing Foundation.

## Simple Idea

Instead of manually running apps on servers, [Kubernetes](ingress.md) manages everything for you:

```text
Your App (containers) → Kubernetes → Servers (cluster)
```

## What It Manages

- Containers (usually built with [Docker](../../containers/docker.md))
- Networking between services
- Scaling — automatically increasing or decreasing instance count
- [Load balancing](../../networking/load-balancing.md)
- Self-healing — restarting failed applications

## Core Components

### Cluster

A group of machines (servers) working together.

### Node

A single machine within the cluster.

### Pod

The smallest deployable unit in [Kubernetes](ingress.md). A pod contains one or more containers.

### Deployment

Defines how many replicas of an app should run and how updates are rolled out.

### Service

Exposes a set of pods to other services or users and handles [load balancing](../../networking/load-balancing.md) between them.

### Ingress

Manages external access — domain and [HTTP](../../networking/http.md)-based routing into the cluster. See [Ingress](ingress.md) for details.

## Example Flow

```text
User → Ingress → Service → Pods (application containers)
```

## Example: Multi-Service Deployment

A platform made up of several services — say an [OCR](../../ai/ingestion/ocr.md) service, a background worker, a text-to-speech service, and an API — maps naturally onto [Kubernetes](ingress.md):

- Each service runs as its own pod (or set of pod replicas).
- [Kubernetes](ingress.md) keeps them running, scales them as traffic increases, and restarts them if they crash.

## Why Use Kubernetes?

### Advantages

- Automatic scaling.
- High availability.
- Self-healing.
- Straightforward integration with [CI/CD](../../devops/ci-cd.md) pipelines.
- Works well with a microservices architecture — see [Monolith vs Microservices](../../backend/architecture/monolith-vs-microservices.md).

### Challenges

- Steep learning curve.
- Setup and operational overhead.
- Requires solid DevOps knowledge.

## Example Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:latest
        ports:
        - containerPort: 3000
```

This runs three replicas of the application.

## K3s: A Lightweight Distribution

**K3s** is a certified, minimal-footprint [Kubernetes](ingress.md) distribution (a single small binary, reduced dependencies) built for resource-constrained or edge environments — a small self-hosted cluster, IoT devices, or simply a team that wants Kubernetes semantics without running the full upstream control-plane stack. It's still real Kubernetes (the same APIs, the same manifests apply), just packaged and configured to be lighter to install and operate; a common path for a smaller platform is to run on [Docker Compose](../../containers/docker-compose.md) initially and adopt K3s as the first step into Kubernetes, before moving to a full managed cluster (EKS/GKE/AKS) if scale later demands it.

## Kubernetes Ecosystem for ML/GPU Workloads

Running AI model-serving workloads on Kubernetes typically pulls in tools beyond the core primitives above — each has its own dedicated note:

| Tool | Purpose |
|---|---|
| **[Helm](helm.md)** | Package manager for Kubernetes manifests — bundles [YAML](../../devops/yaml.md) templates plus configurable values into a versioned, installable "chart" |
| **[Argo CD](argo-cd.md)** | GitOps continuous delivery — syncs the live cluster to match a Git repo's desired state, so deployments happen via a Git commit |
| **[KEDA](keda.md)** | Scales workloads based on external event sources (queue depth, broker backlog) rather than just CPU/memory |
| **[KServe](kserve.md)** | Model-serving framework providing standardized inference APIs, autoscaling (including scale-to-zero), and canary rollouts for ML models |
| **[NVIDIA GPU Operator](nvidia-gpu-operator.md)** | Automates installing/managing everything a node needs to expose GPUs to workloads — drivers, device plugin, GPU monitoring (DCGM) |

Kubernetes' scheduler treats a GPU largely as an indivisible resource to hand to one pod — it doesn't natively solve the fine-grained, VRAM-aware, priority/eviction-based scheduling multiple AI models sharing one GPU actually need. See [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md) for that problem, which typically has to be built as application-level logic even after adopting Kubernetes and the tools above.

## Moving to Kubernetes

For a system already running in containers (e.g. behind a VPS with [Nginx](../../backend/api-gateways/nginx.md) and a process manager like [PM2](../../../commands/pm2.md)), Kubernetes is typically the next step for running everything in production, automating scaling, and managing distributed services cleanly. See [System Design](../../backend/architecture/system-design.md) for broader infrastructure trade-offs.

## One-Line Definition

> Kubernetes is a system that runs and manages containers automatically, at scale.

## Related

- [Ingress](ingress.md)
- [Mesh Architecture](../patterns/mesh-architecture.md)
- [Monolith vs Microservices](../../backend/architecture/monolith-vs-microservices.md)
- [System Design](../../backend/architecture/system-design.md)
- [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md)
- [Health, Liveness & Readiness Checks](../../backend/architecture/health-liveness-readiness.md)
- [Ansible](../../cloud/iac/ansible.md)
- [Helm](helm.md)
- [Argo CD](argo-cd.md)
- [kubectl Commands](../../../commands/kubectl.md)
- [PM2 Commands](../../../commands/pm2.md)
- [KEDA](keda.md)
- [KServe](kserve.md)
- [NVIDIA GPU Operator](nvidia-gpu-operator.md)
