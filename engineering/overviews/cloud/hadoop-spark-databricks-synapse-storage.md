# Hadoop vs. Spark vs. Databricks vs. Synapse vs. ADLS/S3/GCS

The key to understanding this cluster of names: these tools are **mostly not alternatives to each other** — they sit at **different layers** of the same system. Each layer answers a different question:

| Layer | Question | Tools |
|---|---|---|
| **Storage** | Where does the data live? | [ADLS](../../concepts/cloud/azure/adls.md) / [S3](../../concepts/protocols/s3-api.md) / [GCS](../../concepts/cloud/infrastructure/gcs.md) (and, historically, HDFS) |
| **Compute engine** | Who processes the data? | [Spark](../../concepts/distributed-systems/processing/spark.md) (and, historically, MapReduce) |
| **Managed platform** | Who runs and operates the engine for you? | [Databricks](../../concepts/cloud/data/databricks.md) / [Azure Synapse](../../concepts/cloud/azure/azure-synapse.md) |

```
┌──────────────────────────────────────────────┐
│   Managed platform:  Databricks | Synapse     │  ← UI, notebooks, scheduling, permissions
├──────────────────────────────────────────────┤
│   Compute engine:        Apache Spark         │  ← distributed, in-memory computation
├──────────────────────────────────────────────┤
│   Storage:        ADLS | S3 | GCS             │  ← the files themselves (Parquet, Delta)
└──────────────────────────────────────────────┘
```

**Analogy — a factory:**
- **Storage** = the warehouse holding raw materials and finished products.
- **[Spark](../../concepts/distributed-systems/processing/spark.md)** = the workers and machines that process the materials.
- **[Databricks](../../concepts/cloud/data/databricks.md) / [Synapse](../../concepts/cloud/azure/azure-synapse.md)** = a staffing company that brings you the workers and machines and manages them, so you never have to worry about hiring or maintaining them yourself.
- **[Hadoop](../../concepts/distributed-systems/processing/hadoop.md)** = the old factory where the warehouse and the workers are **in the same building** and can't be separated.

---

## 1. Hadoop: the first generation (everything bundled together)

[Hadoop](../../concepts/distributed-systems/processing/hadoop.md) isn't one tool — it's **three components** bundled together:

| Component | Role | What replaced it today |
|---|---|---|
| **HDFS** | Distributed storage, on the disks of the same machines | **[ADLS](../../concepts/cloud/azure/adls.md) / [S3](../../concepts/protocols/s3-api.md) / [GCS](../../concepts/cloud/infrastructure/gcs.md)** |
| **MapReduce** | The processing engine | **[Spark](../../concepts/distributed-systems/processing/spark.md)** |
| **YARN** | Resource management (who gets which machine) | [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md), or the managed platforms themselves |

**MapReduce's problem:** it writes results to **disk** after every step. A 10-step job means 10 rounds of disk reads and writes — very slow.

**HDFS's problem:** storage and compute are **tied to the same machines**. Need more storage space? You have to buy whole machines with processors you don't actually need, and vice versa.

## 2. Spark: the engine that replaced MapReduce

- Processes data **in memory (RAM)** between steps instead of disk, making it far faster.
- Easier interfaces: Python (PySpark), [SQL](../../concepts/databases/relational/sql.md), Scala.
- Supports batch processing, streaming, and machine learning.

**An important point:** [Spark](../../concepts/distributed-systems/processing/spark.md) **replaced MapReduce, not all of [Hadoop](../../concepts/distributed-systems/processing/hadoop.md)**. Initially [Spark](../../concepts/distributed-systems/processing/spark.md) ran **on top of** [Hadoop](../../concepts/distributed-systems/processing/hadoop.md) (reading from HDFS, using YARN for resources). Then, as companies moved to the cloud, [Spark](../../concepts/distributed-systems/processing/spark.md) started reading directly from [ADLS](../../concepts/cloud/azure/adls.md)/S3 and no longer needed [Hadoop](../../concepts/distributed-systems/processing/hadoop.md) at all.

**[Spark](../../concepts/distributed-systems/processing/spark.md) by itself stores nothing.** It's purely an engine — it always needs somewhere to read from and write to.

## 3. ADLS / S3 / GCS: the storage that replaced HDFS

| Service | Cloud | [Spark](../../concepts/distributed-systems/processing/spark.md) URI scheme |
|---|---|---|
| [ADLS Gen2](../../concepts/cloud/azure/adls.md) | [Azure](../../concepts/cloud/azure/azure.md) | `abfss://` |
| [S3](../../concepts/protocols/s3-api.md) | [AWS](../../concepts/cloud/infrastructure/aws.md) | `s3a://` (or `s3://` on some platforms) |
| [GCS](../../concepts/cloud/infrastructure/gcs.md) | Google Cloud | `gs://` |

**The core idea: separation of storage and compute**

| | [Hadoop](../../concepts/distributed-systems/processing/hadoop.md)/HDFS | Modern cloud |
|---|---|---|
| Data lives on | The disks of the same processing machines | An independent storage service |
| When machines are shut down | ❌ You lose access to the data | ✅ The data stays; you only pay for storage |
| Scaling | Buy whole machines | Scale storage and compute independently of each other |
| Cost | Machines running 24/7 | Spin [Spark](../../concepts/distributed-systems/processing/spark.md) up for an hour, then shut it off |

## 4. Databricks and Synapse: who runs Spark for you?

Running Spark yourself means: provisioning machines, managing versions, monitoring, and scaling it all. Managed platforms do this for you.

| | **[Databricks](../../concepts/cloud/data/databricks.md)** | **[Azure Synapse](../../concepts/cloud/azure/azure-synapse.md)** |
|---|---|---|
| **Who built it?** | The company founded by **Spark's own original creators** | Microsoft |
| **Clouds** | [Azure](../../concepts/cloud/azure/azure.md), [AWS](../../concepts/cloud/infrastructure/aws.md), and [GCP](../../concepts/cloud/infrastructure/gcp.md) | [Azure](../../concepts/cloud/azure/azure.md) only |
| **Built on** | An optimized Spark (e.g. the Photon engine) | Spark pools + Microsoft's own [SQL](../../concepts/databases/relational/sql.md) engine |
| **What it adds on top of Spark** | [Delta Lake](../../concepts/cloud/data/delta-lake.md), Unity Catalog for governance, MLflow, AI tooling | Integration with [Azure](../../concepts/cloud/azure/azure.md) services, [SQL](../../concepts/databases/relational/sql.md) pools for data warehousing |
| **Its strength** | The most mature Spark and ML platform | A good fit for staying fully inside the Microsoft ecosystem |

**A note on current [positioning](../../../marketing/concepts/fundamentals/positioning.md):** Microsoft is steering new projects toward **Microsoft Fabric** as its newer analytics platform; Synapse is still supported, but it's no longer the option Microsoft is actively pushing new projects toward. If this matters for a real decision, check Microsoft's latest guidance before committing.

**What they share:** both **run Spark**, and both **read and write to [ADLS](../../concepts/cloud/azure/adls.md)** (or S3/[GCS](../../concepts/cloud/infrastructure/gcs.md), in [Databricks](../../concepts/cloud/data/databricks.md)' case). Neither stores your data in a storage location of its own.

---

## How they work together: an example from a RAG pipeline

```
Document sources (SharePoint, internal systems)
           │
           ▼
   ADLS: bronze/       ← raw PDF files                      [Storage]
           │
           ▼
   Databricks runs Spark:                                    [Platform + Engine]
     • extract text from thousands of PDFs in parallel
     • Arabic normalization
     • chunking + metadata + permissions
           │
           ▼
   ADLS: silver/       ← clean chunks (Delta table)          [Storage]
           │
           ▼
   Spark computes the embeddings
           │
           ▼
   ADLS: gold/         ← embeddings, ready to index           [Storage]
           │
           ▼
   Search index (Azure AI Search / Elasticsearch)
```

Notice that **[ADLS](../../concepts/cloud/azure/adls.md) repeats** at every stage: it's the fixed location, while Spark arrives, processes, and leaves.

---

## The full comparison

| | Layer | Stores data? | Processes data? | Status today |
|---|---|---|---|---|
| **[Hadoop](../../concepts/distributed-systems/processing/hadoop.md)** (HDFS + MapReduce + YARN) | Storage + compute together | ✅ (HDFS) | ✅ (MapReduce) | Legacy, found in older systems |
| **[Spark](../../concepts/distributed-systems/processing/spark.md)** | Compute engine | ❌ | ✅ | The current standard |
| **[ADLS](../../concepts/cloud/azure/adls.md) / [S3](../../concepts/protocols/s3-api.md) / [GCS](../../concepts/cloud/infrastructure/gcs.md)** | Storage | ✅ | ❌ | The current standard |
| **[Databricks](../../concepts/cloud/data/databricks.md)** | Managed platform | ❌ (uses [ADLS](../../concepts/cloud/azure/adls.md)/S3/[GCS](../../concepts/cloud/infrastructure/gcs.md)) | ✅ (via Spark) | The most widely adopted |
| **[Synapse](../../concepts/cloud/azure/azure-synapse.md)** | Managed platform | ❌ (uses [ADLS](../../concepts/cloud/azure/adls.md)) | ✅ (via Spark and [SQL](../../concepts/databases/relational/sql.md)) | Supported; Microsoft is steering toward Fabric |

---

## The one-line summary

**Hadoop** used to bundle storage and processing into one place; the two then split apart: **[ADLS](../../concepts/cloud/azure/adls.md)/S3/[GCS](../../concepts/cloud/infrastructure/gcs.md)** became the storage layer, **Spark** became the processing layer, and **[Databricks](../../concepts/cloud/data/databricks.md)/Synapse** became the easy way to run Spark without managing the underlying infrastructure yourself.

## Related

- [Hadoop](../../concepts/distributed-systems/processing/hadoop.md)
- [Spark](../../concepts/distributed-systems/processing/spark.md)
- [Databricks](../../concepts/cloud/data/databricks.md)
- [Azure Synapse](../../concepts/cloud/azure/azure-synapse.md)
- [ADLS](../../concepts/cloud/azure/adls.md)
- [Amazon S3 API](../../concepts/protocols/s3-api.md)
- [GCS](../../concepts/cloud/infrastructure/gcs.md)
- [Medallion Architecture](../../concepts/cloud/data/medallion-architecture.md) — the Bronze/Silver/Gold pattern the [RAG](../../concepts/ai/rag/rag.md) pipeline example above follows
- [Delta Lake](../../concepts/cloud/data/delta-lake.md) — the table format the Bronze/Silver/Gold layers are usually stored as
