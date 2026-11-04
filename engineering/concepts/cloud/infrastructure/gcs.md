# GCS — Google Cloud Storage

Google Cloud Storage is Google Cloud's [object storage](object-storage.md) service — the [GCP](gcp.md) equivalent of [Amazon S3](../../protocols/s3-api.md) and [Azure Blob Storage](../azure/azure-blob-storage.md)/[ADLS](../azure/adls.md). It stores objects (files) inside flat-namespace **buckets**, and is the standard raw-data landing zone for [GCP](gcp.md) data pipelines feeding BigQuery, Dataproc ([Spark](../../distributed-systems/processing/spark.md)/[Hadoop](../../distributed-systems/processing/hadoop.md)), and Vertex AI.

## Core Concepts

| Term | Meaning |
|---|---|
| **Bucket** | A globally-unique top-level container for objects — like an S3 bucket or an [ADLS](../azure/adls.md) container |
| **Object** | A stored file — a name (key) + binary data + metadata, immutable once written (a new write creates a new object generation) |
| **Project** | Every bucket belongs to a [GCP](gcp.md) project, which is also the billing and IAM boundary |
| **Location type** | Region, dual-region, or multi-region — affects latency, availability, and cost |
| **Storage class** | Standard / Nearline / Coldline / Archive — the same hot-to-archive cost/access-speed tradeoff as [Azure](../azure/azure.md)'s Hot/Cool/Cold/Archive tiers |

Like S3 and unlike [ADLS Gen2](../azure/adls.md), GCS buckets are natively a **flat namespace** — a `/` in an object name is just a character, not a real directory. Google's [Hadoop](../../distributed-systems/processing/hadoop.md) Connector for GCS (used by Dataproc/[Spark](../../distributed-systems/processing/spark.md)) simulates directory semantics on top of this flat namespace the same way S3's [Hadoop](../../distributed-systems/processing/hadoop.md) connector does, rather than GCS having a true hierarchical namespace built in the way [ADLS](../azure/adls.md) Gen2 does.

## URI Format

```
gs://<bucket>/<path>
```

```python
# Reading from GCS in a Spark/Dataproc job
df = spark.read.parquet("gs://my-bucket/raw/documents/2024/")
```

## Access Control

Two overlapping permission systems, mirroring the same two-layer pattern [ADLS](../azure/adls.md) uses:
- **Cloud IAM** — coarse-grained: roles like Storage Object Viewer/Admin granted at the project, bucket, or (with conditions) prefix level
- **ACLs** (legacy, largely superseded by IAM + uniform bucket-level access) — per-object/bucket access grants; Google recommends IAM over ACLs for new buckets

For enterprise [RAG](../../ai/rag/rag.md): as with [ADLS](../azure/adls.md) and S3, GCS enforces access to the *objects themselves*, not to search results derived from them — an application reading from GCS into a vector index must independently propagate and enforce document-level permissions at retrieval time; GCS has no visibility into or control over what happens after a file is read.

## GCS vs S3 vs ADLS Gen2

| | GCS | Amazon S3 | [ADLS](../azure/adls.md) Gen2 |
|---|---|---|---|
| Namespace | Flat (directory-like prefixes simulated) | Flat (directory-like prefixes simulated) | Hierarchical (real folders, atomic rename) |
| Fine-grained permissions | IAM conditions; legacy ACLs | IAM policies | [POSIX ACLs](../../security/authorization/posix-acls.md) (true per-file/folder) |
| Native big-data connector | [Hadoop](../../distributed-systems/processing/hadoop.md) Connector (`gs://`) | `s3a://` ([Hadoop](../../distributed-systems/processing/hadoop.md)-S3A connector) | ABFS (`abfss://`) |
| Primary ecosystem | [GCP](gcp.md) / BigQuery / Dataproc / Vertex AI | [AWS](aws.md) / EMR / Redshift | [Azure](../azure/azure.md) / [Databricks](../data/databricks.md) / Synapse |

## Related

- [Google Cloud Platform (GCP)](gcp.md) — the provider GCS belongs to
- [Amazon S3 API](../../protocols/s3-api.md) — the closest cross-cloud equivalent; GCS's API is deliberately S3-interoperable enough that some S3 clients work against it with an endpoint change
- [ADLS](../azure/adls.md) — the [Azure](../azure/azure.md) equivalent, with a genuinely hierarchical namespace GCS and S3 both lack natively
- [Azure Blob Storage](../azure/azure-blob-storage.md) — the more direct flat-object-storage analog to GCS ([ADLS](../azure/adls.md) Gen2 is Blob Storage plus a hierarchical namespace layered on top)
