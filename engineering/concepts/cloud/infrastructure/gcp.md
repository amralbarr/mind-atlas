# Google Cloud Platform (GCP)

GCP is Google's cloud platform, generally regarded as strongest for AI/ML workloads and large-scale data analytics — a reflection of it running on the same infrastructure Google's own internal systems (Search, YouTube) use. See [Cloud Providers](../../../overviews/cloud/cloud-providers.md) for how it compares to [AWS](aws.md) and [Azure](../azure/azure.md).

## Core Concepts

| Term | Meaning |
|---|---|
| **Project** | GCP's top-level container for resources and billing — the rough equivalent of an [AWS](aws.md) account or an [Azure](../azure/azure.md) subscription |
| **Region / Zone** | Same structure as [AWS](aws.md)/[Azure](../azure/azure.md) — a region contains multiple isolated zones for fault tolerance |
| **IAM** | GCP's access-control system — roles (predefined or custom) bound to identities (users, service accounts, groups) at the project/resource level |
| **Service Account** | A non-human identity used by applications/VMs to authenticate to GCP APIs — the standard way workloads (not people) get scoped access |

## Core Services

| Service | Purpose | Analogous to |
|---|---|---|
| **Compute Engine** | [Virtual machines](virtual-machines.md) | [AWS](aws.md) EC2, [Azure](../azure/azure.md) VM |
| **Cloud Storage** | [Object storage](object-storage.md) | [AWS](aws.md) S3, [Azure Blob Storage](../azure/azure-blob-storage.md) |
| **Cloud [SQL](../../databases/relational/sql.md) / Spanner** | Managed relational databases (Spanner: globally distributed [SQL](../../databases/relational/sql.md)) | [AWS](aws.md) RDS, [Azure](../azure/azure.md) [SQL](../../databases/relational/sql.md) |
| **BigQuery** | Serverless, massively parallel data warehouse for analytics at scale | No direct [AWS](aws.md)/[Azure](../azure/azure.md) equivalent at the same scale/pricing model |
| **Cloud Run** | Fully managed serverless containers — deploy a container image directly, scale to zero | AWS Fargate, [Azure](../azure/azure.md) Container Apps |
| **Vertex AI** | Managed ML platform — training, hosting, and serving models | AWS SageMaker, Azure AI |
| **Cloud [Pub/Sub](../../distributed-systems/messaging/publish-subscribe.md)** | Managed messaging — see [Google Cloud Pub/Sub](../../distributed-systems/messaging/google-pubsub.md) |
| **GKE** | Managed [Kubernetes](../../distributed-systems/kubernetes/ingress.md), generally considered the most mature managed [Kubernetes](../../distributed-systems/kubernetes/ingress.md) offering of the three major clouds | AWS EKS, Azure AKS |

## gcloud CLI — Basic Usage

```bash
gcloud auth login
gcloud config set project my-project-id

gcloud compute instances list
gcloud storage ls gs://my-bucket
```

## Deploying a Container to Cloud Run

```bash
gcloud run deploy my-service \
  --image gcr.io/my-project-id/my-service:latest \
  --region us-central1 \
  --allow-unauthenticated
```

Cloud Run scales the container to zero when idle and back up on request — no cluster to provision or manage, in contrast to running the same container on GKE.

## Common Questions

**Why is GCP considered the AI/ML-strongest of the three major clouds?**
> Vertex AI, BigQuery's analytics performance, and GKE's [Kubernetes](../../distributed-systems/kubernetes/ingress.md) maturity reflect Google's own internal use of these same systems at massive scale (Search, YouTube) — the tooling was built for and battle-tested on Google's own AI/data workloads before being offered externally, which shows up in the depth of the ML/data-specific product line compared to AWS/Azure's broader-but-shallower equivalents.

**When would a team pick GCP over AWS despite AWS's larger ecosystem?**
> When the workload is genuinely AI/ML- or big-data-analytics-heavy (BigQuery, Vertex AI, GKE) and that outweighs AWS's advantage in sheer breadth of services and community tutorials/support — see [Cloud Providers](../../../overviews/cloud/cloud-providers.md) for the fuller decision table.

## Related

- [Cloud Providers](../../../overviews/cloud/cloud-providers.md)
- [Microsoft Azure](../azure/azure.md)
- [AWS](aws.md)
- [GCS](gcs.md) — [Google Cloud Storage](gcs.md), GCP's [object storage](object-storage.md) service
- [Google Cloud Pub/Sub](../../distributed-systems/messaging/google-pubsub.md)
