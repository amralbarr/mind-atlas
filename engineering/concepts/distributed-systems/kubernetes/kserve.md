# KServe

KServe is a model-serving framework built on [Kubernetes](ingress.md) that provides a standardized way to deploy, autoscale, and roll out ML models, instead of every team hand-building its own inference deployment, routing, and scaling logic. See [Kubernetes Basics](kubernetes-basics.md) for the underlying platform and [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md) for the scheduling problem KServe's [Kubernetes](ingress.md)-level autoscaling does *not* solve on its own.

## Core Concepts

| Term | Meaning |
|---|---|
| **InferenceService** | KServe's core custom resource (`serving.kserve.io/v1beta1`) — declares a model's storage location, framework/runtime, and resource requests; KServe generates the Deployment, Service, and autoscaling config underneath it |
| **Predictor** | The component that actually loads the model and serves inference requests — configured per-framework (scikit-learn, TensorFlow, PyTorch, Hugging Face, a custom container) |
| **Standardized inference protocol** | KServe exposes a consistent `v1`/`v2` (and OpenAI-compatible, for [LLMs](../../ai/generation/llm.md)) [HTTP](../../networking/http.md)/[gRPC](../../backend/api/grpc.md) API regardless of the underlying framework, so clients don't need framework-specific integration code |
| **Scale-to-zero** | Like [KEDA](keda.md), an idle InferenceService can scale down to zero replicas and cold-start back up on the next request — meaningful for expensive GPU-backed models that shouldn't sit warm 24/7 |
| **Canary rollout** | Traffic can be split between two model versions by percentage, directly via the InferenceService spec, without a separate service mesh configuration |

## Deploying a Model

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: sklearn-iris
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: gs://kfserving-examples/models/sklearn/1.0/model
      resources:
        requests:
          cpu: "1"
          memory: 2Gi
```

```bash
kubectl apply -f inferenceservice.yaml
kubectl get inferenceservice sklearn-iris
# Shows the auto-generated, ready-to-use inference URL
```

## Deploying an LLM (Hugging Face Runtime)

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: qwen-chat
spec:
  predictor:
    model:
      modelFormat:
        name: huggingface
      storageUri: hf://Qwen/Qwen2.5-0.5B-Instruct
      resources:
        limits:
          nvidia.com/gpu: "1"
```

The `nvidia.com/gpu` resource request is what actually gets a GPU allocated to the pod — see [NVIDIA GPU Operator](nvidia-gpu-operator.md) for what makes GPUs visible to [Kubernetes](ingress.md) as a schedulable resource in the first place.

## Canary Traffic Split

```yaml
spec:
  predictor:
    canaryTrafficPercent: 10   # 10% of traffic to the new revision, 90% to the current one
    model:
      storageUri: gs://.../model-v2
```

## Common Questions

**Does KServe solve [GPU scheduling](../../ai/infrastructure/gpu-scheduling.md) for multiple models sharing one GPU?**
> No — KServe (via [Kubernetes](ingress.md)) treats a GPU as an indivisible unit assigned to one pod. Fine-grained, VRAM-aware sharing of one physical GPU across several models still has to be built as application-level logic; see [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md) for that problem.

**When is KServe overkill compared to just wrapping a model in a [FastAPI](../../programming/python/fastapi.md)/[Flask](../../programming/python/flask.md) container?**
> A hand-rolled container is fine for one model with simple, stable traffic. KServe earns its complexity once there are multiple models needing consistent autoscaling (including scale-to-zero), canary rollouts, and a uniform inference API across different frameworks — reimplementing all of that per model is the actual cost KServe removes.

## Related

- [Kubernetes Basics](kubernetes-basics.md)
- [NVIDIA GPU Operator](nvidia-gpu-operator.md)
- [KEDA](keda.md)
- [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md)
- [Model Lifecycle Management](../../ai/infrastructure/model-lifecycle-management.md)
