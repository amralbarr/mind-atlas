# NVIDIA GPU Operator

The NVIDIA GPU Operator automates everything a [Kubernetes](ingress.md) node needs to expose its GPUs to workloads — drivers, the container toolkit, the device plugin, and monitoring — instead of manually installing and keeping each of those in sync on every GPU node by hand. See [Kubernetes Basics](kubernetes-basics.md) for the platform it plugs into, and [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md) for the scheduling problem it does *not* solve (it makes GPUs visible and healthy; it doesn't decide which model should run on which GPU).

## Core Concepts

| Term | Meaning |
|---|---|
| **NVIDIA driver** | The kernel-level driver a node needs before anything can talk to its GPU at all — normally installed manually per-node/per-OS-image; the Operator installs and upgrades it via a containerized DaemonSet instead |
| **NVIDIA Container Toolkit** | Lets a container runtime (containerd, CRI-O) actually expose a host GPU inside a container |
| **Device plugin** | The [Kubernetes](ingress.md) component that advertises `nvidia.com/gpu` as a schedulable resource, so a pod can request `resources.limits."nvidia.com/gpu": 1` like it would CPU or memory |
| **DCGM Exporter** | Exposes per-GPU telemetry (utilization, VRAM, temperature, power) in [Prometheus](../../backend/observability/prometheus.md) format — see [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md#gpu-telemetry) for why this matters more than parsing `nvidia-smi` output |
| **Operator pattern** | A [Kubernetes](ingress.md) controller that continuously reconciles a piece of infrastructure (here: GPU drivers/toolkit/monitoring) to a desired state across every matching node, rather than a one-time install script |

## Installing (via Helm)

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator --create-namespace
```

See [Helm](helm.md) for what a chart install like this is actually doing under the hood.

## Requesting a GPU in a Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-inference
spec:
  containers:
    - name: model-server
      image: my-registry/model-server:latest
      resources:
        limits:
          nvidia.com/gpu: "1"   # the device plugin, installed by the Operator, makes this schedulable
```

[Kubernetes](ingress.md) schedules this pod only onto a node advertising at least one free `nvidia.com/gpu`, and the Operator ensures every GPU node has the driver/toolkit/plugin needed for that resource to actually work once scheduled.

## Verifying GPU Visibility

```bash
kubectl get nodes -o json | jq '.items[].status.allocatable."nvidia.com/gpu"'

# Confirm the Operator's own components are healthy
kubectl get pods -n gpu-operator
```

## Common Questions

**Without the GPU Operator, is GPU support in [Kubernetes](ingress.md) just missing entirely?**
> No — it's possible to install the NVIDIA driver, container toolkit, and device plugin manually on each GPU node. The Operator's value is doing that consistently and automatically across a fleet of nodes (including new nodes joining the cluster, and driver upgrades), rather than a manual, easy-to-drift, per-node setup process.

**Does this Operator make [GPU scheduling](../../ai/infrastructure/gpu-scheduling.md) "smart" (e.g. multiple models sharing one GPU efficiently)?**
> No — it makes a GPU visible and usable as an indivisible schedulable resource, which is a prerequisite, not a solution to fine-grained sharing. Actual VRAM-aware, priority-based sharing of one GPU across multiple models is a separate problem; see [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md).

## Related

- [Kubernetes Basics](kubernetes-basics.md)
- [Helm](helm.md)
- [KServe](kserve.md)
- [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md)
