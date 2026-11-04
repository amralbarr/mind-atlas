# ADLS — Azure Data Lake Storage

Azure Data Lake Storage Gen2 (ADLS Gen2) is Microsoft's scalable cloud [object storage](../infrastructure/object-storage.md) for big data analytics — built on top of [Azure Blob Storage](azure-blob-storage.md) with a hierarchical namespace (folders, not just flat key prefixes) and [Hadoop](../../distributed-systems/processing/hadoop.md)-compatible filesystem semantics. It is the standard raw storage layer for [Azure](azure.md) data engineering workloads and the primary data source for [Azure Databricks](../data/databricks.md).

## What It Is

ADLS is [object storage](../infrastructure/object-storage.md) (like [Amazon S3](../../protocols/s3-api.md) or [Google Cloud Storage](../infrastructure/gcs.md)) with extra capabilities:

```
Azure Blob Storage (base: objects in containers)
    +
Hierarchical Namespace (real folders, atomic renames, directory operations)
    +
POSIX-style ACLs (fine-grained per-file/folder permissions)
    =
ADLS Gen2
```

Files are organized into **storage accounts → containers → directories → files**. A container in ADLS is equivalent to an [S3](../../protocols/s3-api.md) bucket or a [GCS](../infrastructure/gcs.md) bucket.

## Key Properties

| Property                                                     | Details                                                                                                                                                                                                              |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Hierarchical namespace**                                   | Real directory structure — atomic rename of a directory (fast), not object-key tricks                                                                                                                                |
| **[POSIX ACLs](../../security/authorization/posix-acls.md)** | Per-file and per-directory read/write/execute permissions for users and service principals                                                                                                                           |
| **[Tiered storage](../infrastructure/storage-tiers.md)**     | Hot / Cool / Cold / Archive tiers — cost vs access speed tradeoff                                                                                                                                                    |
| **Massive scale**                                            | Exabyte-scale; designed for parallel reads by [Spark](../../distributed-systems/processing/spark.md), [Hadoop](../../distributed-systems/processing/hadoop.md)                                                       |
| **Protocol support**                                         | [Azure Blob](azure-blob-storage.md) [REST](../../backend/api/rest.md) API + ABFS (`abfss://`) for [Hadoop](../../distributed-systems/processing/hadoop.md)/[Spark](../../distributed-systems/processing/spark.md) + NFS 3.0 for file-based access |
| **Integration**                                              | Native integration with [Azure Databricks](../data/databricks.md), [Azure Synapse](azure-synapse.md), [Azure Data Factory](azure-data-factory.md), [Azure ML](azure-ml.md)                                           |

## ABFS URI Format

When [Databricks](../data/databricks.md) or [Spark](../../distributed-systems/processing/spark.md) accesses ADLS:

```
abfss://<container>@<storage-account>.dfs.core.windows.net/<path>
```

Example:
```python
# In a Databricks notebook
df = spark.read.parquet("abfss://raw@mystorageaccount.dfs.core.windows.net/documents/2024/")
```

## Access Control

Two overlapping permission systems:
- **[Azure RBAC](azure-rbac.md)** — coarse-grained: Storage Blob Data Reader/Contributor roles on the whole storage account or container
- **[POSIX ACLs](../../security/authorization/posix-acls.md)** — fine-grained: per-file/directory, set with [Azure](azure.md) CLI or Storage Explorer

For enterprise [RAG](../../ai/rag/rag.md): document-level permissions in ADLS can map to retrieval-time filters, but the application must read those permissions and apply them — ADLS itself does not enforce them inside the [RAG](../../ai/rag/rag.md) pipeline.

## Medallion Layers on ADLS

In a [Databricks](../data/databricks.md) + ADLS architecture, the three [medallion architecture](../data/medallion-architecture.md) layers (Bronze/Silver/Gold) are physically stored as [Delta Lake](../data/delta-lake.md) tables on ADLS:

```
adls://raw/bronze/documents/          ← raw ingested PDFs / JSON
adls://processed/silver/documents/    ← cleaned, chunked, metadata-enriched
adls://curated/gold/embeddings/       ← embedding vectors ready for indexing
```

## ADLS vs S3 vs GCS vs Azure Blob Storage

|                                                                                                                          | ADLS Gen2                                   | [Amazon S3](../../protocols/s3-api.md) | [GCS](../infrastructure/gcs.md) | [Azure Blob Storage](azure-blob-storage.md) |
| ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- | -------------------------------------- | ------------------------------- | ------------------------------------------- |
| Hierarchical namespace                                                                                                   | Yes (real folders)                          | No (prefix tricks)                     | No (prefix tricks)              | No (unless ADLS enabled)                    |
| [POSIX ACLs](../../security/authorization/posix-acls.md)                                                                 | Yes                                         | No (IAM policies only)                 | No (IAM + legacy ACLs)          | No                                          |
| [Hadoop](../../distributed-systems/processing/hadoop.md) / [Spark](../../distributed-systems/processing/spark.md) native | Yes (ABFS)                                  | Yes (`s3a://`)                         | Yes (`gs://`)                   | Limited                                     |
| Primary ecosystem                                                                                                        | [Azure](azure.md) / [Databricks](../data/databricks.md) | [AWS](../infrastructure/aws.md) / EMR                              | [GCP](../infrastructure/gcp.md) / BigQuery / Dataproc       | [Azure](azure.md) (non-analytics)                       |

## Related
- [Databricks](../data/databricks.md)
- [Azure Synapse](azure-synapse.md) — the [SQL](../../databases/relational/sql.md)-and-[Spark](../../distributed-systems/processing/spark.md) analytics platform that also reads/writes ADLS
- [Azure Data Factory](azure-data-factory.md) — the pipeline/orchestration service that most commonly lands data into ADLS
- [Azure ML](azure-ml.md) — another native-integration consumer of ADLS-stored training data
- [Azure Blob Storage](azure-blob-storage.md) — the base layer ADLS Gen2 is built on top of
- [Amazon S3](../../protocols/s3-api.md) — the [AWS](../infrastructure/aws.md) equivalent
- [GCS](../infrastructure/gcs.md) — the [GCP](../infrastructure/gcp.md) equivalent
- [Azure RBAC](azure-rbac.md) — the coarse-grained half of ADLS's two-layer access control
- [POSIX ACLs](../../security/authorization/posix-acls.md) — the fine-grained half, explained on its own
- [Spark](../../distributed-systems/processing/spark.md) / [Hadoop](../../distributed-systems/processing/hadoop.md) — the processing engines ADLS is designed for parallel reads by
- [Storage Tiers](../infrastructure/storage-tiers.md) — the Hot/Cool/Cold/Archive cost-vs-access-speed trade-off, compared across ADLS/S3/[GCS](../infrastructure/gcs.md)
- [Medallion Architecture](../data/medallion-architecture.md) — the Bronze/Silver/Gold data-organization pattern used on ADLS
- [Delta Lake](../data/delta-lake.md) — the [ACID](../../databases/relational/acid.md) table format the medallion layers are physically stored as
- [Governed Data](../data/governed-data.md) — ADLS ACLs are one enforcement point for data governance; what "governed" means in practice
- [Hadoop vs. Spark vs. Databricks vs. Synapse vs. ADLS/S3/GCS](../../../overviews/cloud/hadoop-spark-databricks-synapse-storage.md) — the full layered picture this file is one piece of
- [Azure AI Foundry](azure-ai-foundry.md)
- [Microsoft Entra ID](microsoft-entra-id.md) — service principals for ADLS access
