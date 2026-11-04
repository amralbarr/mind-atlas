# Azure Compute Hosting Options — Container Apps vs. App Service vs. AKS

All three can run the exact same container image. The real decision isn't "which one *can* run my app" — all of them can — it's how much orchestration control the workload genuinely needs, weighed against how much operational burden the team is willing to own for that control.

## The Comparison

| | Container Apps | App Service | AKS |
|---|---|---|---|
| **What it is** | Serverless container hosting, built on a managed [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md) + [KEDA](../../concepts/distributed-systems/kubernetes/keda.md) + Envoy underneath, with the cluster itself fully abstracted away | A managed web-app platform — upload a container or code package, [Azure](../../concepts/cloud/azure/azure.md) runs it behind a built-in web server and load balancer | Full, self-managed [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md) — you see and configure the cluster, node pools, and the [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md) API directly |
| **Scaling** | Event-driven scale-to-zero via [KEDA](../../concepts/distributed-systems/kubernetes/keda.md) ([HTTP](../../concepts/networking/http.md) traffic, queue depth, CPU, or custom metrics) — built in, no extra setup | Autoscale rules based on CPU/memory/schedule; scale-to-zero only on certain plans, not the general case | Full control via [HPA](../../concepts/distributed-systems/kubernetes/kubernetes-basics.md)/[KEDA](../../concepts/distributed-systems/kubernetes/keda.md)/cluster autoscaler — but you configure and own all of it |
| **Orchestration control** | Minimal — no direct [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md) API access, no custom resources, no service mesh configuration | None — not [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md)-based at all; no multi-container pod-level orchestration | Full — custom resources, operators, service mesh, [Helm](../../concepts/distributed-systems/kubernetes/helm.md) charts, [ArgoCD](../../concepts/distributed-systems/kubernetes/argo-cd.md)-style GitOps, anything the Kubernetes ecosystem supports |
| **Networking** | [VNet](../../concepts/cloud/azure/azure-vnet.md) integration and [private endpoints](../../concepts/cloud/azure/azure-vnet.md) supported, simplified compared to raw Kubernetes networking | [VNet](../../concepts/cloud/azure/azure-vnet.md) integration available, simplest networking model of the three | Full control — [NSGs](../../concepts/cloud/azure/azure-nsg.md), network policies, [ingress](../../concepts/distributed-systems/kubernetes/ingress.md), service mesh — and full responsibility for configuring them correctly |
| **Multi-container coordination** | Supports sidecars and Dapr-based service-to-service patterns within one Container App | Not designed for this — one app, one container (or a small sidecar set), not a multi-service mesh | Native — this is what Kubernetes pods/services/deployments exist to coordinate |
| **GPU support** | Not available | Not available | Available, via node pools with GPU SKUs and the [NVIDIA GPU Operator](../../concepts/distributed-systems/kubernetes/nvidia-gpu-operator.md) — the only one of the three that can host a self-hosted inference server like [vLLM](../../concepts/ai/infrastructure/vllm.md) |
| **Operational burden** | Low — no cluster to patch, upgrade, or size | Lowest — simplest mental model, closest to "just deploy my app" | High — node pool sizing, Kubernetes version upgrades, cluster-level security patching are all the team's own responsibility |
| **Cost at idle** | Scales to zero — pay nothing when there's no traffic | Pay for the App Service Plan continuously, regardless of traffic, unless on a scale-to-zero-capable plan | Pay for provisioned nodes continuously, regardless of pod-level idle time, unless cluster autoscaler shrinks the node count |

## The Decision, in Practice

**Container Apps is the default for most new containerized microservices and APIs** — including a [RAG](../../concepts/ai/rag/rag.md) API — specifically because it gets most of Kubernetes' practical benefit (event-driven scaling, sidecars, service-to-service calls) without the cluster-management burden. It's the right default whenever the workload is a normal containerized service with no need for GPU nodes, custom Kubernetes resources, or a service mesh.

**App Service fits best when the workload is closer to "one web app," not a set of coordinating microservices** — a single API or web frontend, especially one that benefits from App Service's built-in deployment slots (staging vs. production, easy swap) and its simpler, more web-app-shaped mental model. It's a weaker fit the moment the architecture needs more than one cooperating container.

**AKS is justified specifically when the workload needs something Container Apps' [abstraction](../../concepts/programming/fundamentals/abstraction.md) hides** — GPU nodes for a self-hosted model (the clearest hard requirement among the three), custom Kubernetes operators, fine-grained service-mesh traffic control, or an organization that already runs AKS elsewhere and has the platform expertise and tooling ([Helm](../../concepts/distributed-systems/kubernetes/helm.md), GitOps) to justify adding one more workload to an existing cluster rather than standing up a separate Container Apps environment. Choosing AKS *without* one of these concrete reasons is usually paying for operational complexity the workload doesn't actually need.

## Common Questions

**If Container Apps is "serverless Kubernetes," why would anyone ever need AKS instead?**
> Because Container Apps deliberately hides the Kubernetes API and cluster internals to get its simplicity — which is exactly what a team loses access to. The moment a workload needs a GPU node pool, a custom Kubernetes operator, or direct control over scheduling/networking at the pod level, that [abstraction](../../concepts/programming/fundamentals/abstraction.md) becomes a limitation rather than a convenience, and AKS's full control becomes the actual requirement, not just a preference.

**Does "scale-to-zero" on Container Apps mean the first request after idle is instant?**
> No — scaling from zero still pays a cold-start cost (pulling the image, starting the container), the same cold-start trade-off [Azure Functions](../../concepts/cloud/azure/azure-functions.md)' Consumption plan has. For a latency-sensitive [RAG](../../concepts/ai/rag/rag.md) API where a cold first request is unacceptable, a minimum-replica-count setting (never scaling fully to zero) trades away some of the cost savings for consistent latency.

**Is choosing AKS ever the "safe default" the way Container Apps is for simpler services?**
> No — AKS should be the deliberate choice when a specific requirement demands it, not a default reached for because it's the most powerful or most familiar option. Defaulting to AKS for a workload that doesn't need its control surface means carrying node-pool and cluster-upgrade operational burden for no actual benefit over Container Apps.

## Related

- [Azure RAG Platform Map](../../interview/interview-01/22-azure-rag-platform-map.md) — marks Container Apps as the default compute choice for the application layer, per this comparison
- [Kubernetes Basics](../../concepts/distributed-systems/kubernetes/kubernetes-basics.md) — the orchestration model AKS exposes directly and Container Apps abstracts away
- [KEDA](../../concepts/distributed-systems/kubernetes/keda.md) — the event-driven autoscaler underneath Container Apps' scale-to-zero behavior
- [NVIDIA GPU Operator](../../concepts/distributed-systems/kubernetes/nvidia-gpu-operator.md) — what AKS needs to expose GPU nodes to a self-hosted inference workload
- [GPU-Aware Scheduling](../../concepts/ai/infrastructure/gpu-scheduling.md) — the scheduling problem that only comes up once AKS + GPU nodes are in play
- [Helm](../../concepts/distributed-systems/kubernetes/helm.md) / [ArgoCD](../../concepts/distributed-systems/kubernetes/argo-cd.md) — the deployment tooling AKS's full Kubernetes control makes available, that Container Apps and App Service don't need
- [Azure Functions](../../concepts/cloud/azure/azure-functions.md) — the fourth [Azure](../../concepts/cloud/azure/azure.md) compute option, for single-function event-driven workloads rather than a full API service
- [Azure Virtual Network (VNet)](../../concepts/cloud/azure/azure-vnet.md) — the private networking layer all three integrate with, at different levels of configurability
