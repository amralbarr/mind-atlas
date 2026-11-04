# KEDA (Kubernetes Event-Driven Autoscaling)

KEDA extends [Kubernetes](ingress.md)' native autoscaling to scale workloads based on external event sources — queue depth, message broker backlog, a database query result, a cron schedule — instead of only CPU/memory utilization. See [Kubernetes Basics](kubernetes-basics.md) for the Horizontal Pod Autoscaler (HPA) it builds on rather than replaces.

## Core Concepts

| Term | Meaning |
|---|---|
| **ScaledObject** | KEDA's custom resource describing what to scale (a Deployment) and which external metric(s) drive that scaling |
| **Scaler** | A pluggable adapter for one specific event source ([Kafka](../messaging/kafka.md), [RabbitMQ](../messaging/rabbitmq.md), Redis, [Prometheus](../../backend/observability/prometheus.md), [Azure Service Bus](../messaging/azure-service-bus.md), cron, and dozens more) that KEDA polls to produce a scaling metric |
| **Activation** | KEDA can scale a deployment from **zero** replicas up when an event source has backlog, and back to zero when it's empty — something the standard HPA can't do on its own (HPA only scales among an existing minimum ≥1) |
| **Cooldown period** | How long to wait with no events before scaling back down, avoiding rapid scale-up/scale-down thrashing on a bursty source |

## Scaling on Queue Depth

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: order-worker-scaler
spec:
  scaleTargetRef:
    name: order-worker           # the Deployment to scale
  minReplicaCount: 0
  maxReplicaCount: 20
  cooldownPeriod: 30
  triggers:
    - type: rabbitmq
      metadata:
        queueName: orders.fulfillment
        host: amqp://guest:guest@rabbitmq.default.svc:5672
        queueLength: "5"          # target ~5 messages per replica
```

With `minReplicaCount: 0`, the `order-worker` Deployment scales to zero pods when the queue is empty — genuinely no compute cost while idle — and KEDA spins up replicas the moment messages start arriving, proportionally to queue depth.

## How KEDA Fits with the HPA

```text
External event source (queue depth, Kafka lag, cron)
        ↓
KEDA scaler polls it, exposes as a custom metric
        ↓
Kubernetes HPA (KEDA manages this for you) scales the Deployment
```

KEDA doesn't replace the HPA — it creates and manages an HPA behind the scenes, feeding it a metric from whatever external source you configure, and additionally handles the zero-to-one activation the HPA alone cannot do.

## Common Questions

**Why not just use CPU-based autoscaling for a queue worker?**
> A worker pulling jobs from a queue may sit at low CPU while still having a large backlog waiting (e.g. each job is [I/O](../../programming/fundamentals/io.md)-bound, waiting on an external API) — CPU utilization doesn't reflect that backlog at all. Scaling directly on queue depth reacts to the actual signal that matters: how much work is waiting, not how busy the existing replicas happen to be.

**Does KEDA work with any message broker?**
> It ships scalers for most common ones out of the box ([RabbitMQ](../messaging/rabbitmq.md), [Kafka](../messaging/kafka.md), [SQS](../messaging/sqs.md), [Azure](../../cloud/azure/azure.md) Service Bus, Redis) — see [Message Brokers](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) for what each of those is. For anything without a built-in scaler, KEDA also supports a generic [Prometheus](../../backend/observability/prometheus.md)-metric scaler or a custom metrics API.

## Related

- [Kubernetes Basics](kubernetes-basics.md)
- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md)
