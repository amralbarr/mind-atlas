# Databricks

Databricks is a unified data analytics platform built on [Apache Spark](../../distributed-systems/processing/spark.md) — managed [Spark](../../distributed-systems/processing/spark.md) clusters, a collaborative notebook environment, [Delta Lake](delta-lake.md) storage, and MLflow for ML experiment tracking, all in one managed service. It runs on [Azure](../azure/azure.md) ([Azure](../azure/azure.md) Databricks), [AWS](../infrastructure/aws.md), and [GCP](../infrastructure/gcp.md).

## What It Is

Databricks sits between raw cloud storage ([ADLS](../azure/adls.md), S3) and downstream analytics/ML:

```
Raw Data (ADLS / S3 / GCS)
    ↓
Databricks (Spark processing, Delta Lake, notebooks)
    ↓
Cleaned / transformed data → ML models / BI dashboards / downstream APIs
```

It is the dominant platform for large-scale data engineering and ML at enterprise data teams — the equivalent of having a managed [Spark](../../distributed-systems/processing/spark.md) cluster with a collaborative IDE, versioned data tables ([Delta Lake](delta-lake.md)), and MLOps tooling bundled together.

## Core Components

| Component                   | What it does                                                                                                                                                        |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[Apache Spark](../../distributed-systems/processing/spark.md)**            | Distributed compute engine — processes data in parallel across many nodes. PySpark is Python on top of [Spark](../../distributed-systems/processing/spark.md).                                                       |
| **[Delta Lake](delta-lake.md)**              | Open-source storage layer on top of Parquet files — adds [ACID](../../databases/relational/acid.md) transactions, schema enforcement, versioning (time travel), and upsert/merge operations to data lakes |
| **Databricks Notebooks**    | Collaborative Jupyter-style notebooks (Python, [SQL](../../databases/relational/sql.md), Scala, R) with shared cluster execution                                                                         |
| **Databricks [SQL](../../databases/relational/sql.md)**          | [SQL](../../databases/relational/sql.md) analytics directly over [Delta Lake](delta-lake.md) tables — BI tools connect via ODBC/JDBC                                                                                      |
| **MLflow**                  | Open-source MLOps: experiment tracking, model registry, model serving. Databricks manages MLflow as a first-class service                                           |
| **Unity Catalog**           | Centralized data governance — tables, columns, access policies, lineage across all workspaces                                                                       |
| **Delta Live Tables (DLT)** | Declarative ETL pipelines with automatic dependency management and data quality checks                                                                              |
| **Databricks Workflows**    | Orchestrate notebooks and jobs on a schedule (similar to [Airflow](../../ai/infrastructure/airflow.md) but native to Databricks)                                                                          |

## Delta Lake — Why It Matters

Plain data lakes (Parquet files on S3/[ADLS](../azure/adls.md)) have no transactions, no schema enforcement, no way to update a row. [Delta Lake](delta-lake.md) adds:
- **[ACID](../../databases/relational/acid.md) transactions** — concurrent reads/writes without corruption
- **Schema evolution** — add columns without rewriting the whole table
- **Time travel** — `SELECT * FROM table VERSION AS OF 5` — query any historical version
- **MERGE / UPSERT** — update specific rows, not just append
- **Data quality** — `CONSTRAINT` checks that reject bad records at write time

This is what makes a data lake behave more like a database — hence "Lakehouse architecture."

## Medallion Architecture (Bronze / Silver / Gold)

The standard data layering pattern in Databricks:

```
Bronze  — raw ingested data, as-is from source (immutable, append-only)
    ↓
Silver  — cleaned, deduplicated, schema-validated, joined
    ↓
Gold    — business-level aggregates, feature tables, ML-ready datasets
```

Each layer is a set of [Delta Lake](delta-lake.md) tables. ETL pipelines (Delta Live Tables or notebooks) transform data layer by layer.

## PySpark — The Python API

Most Databricks work is done in PySpark — Python code that compiles to [Spark](../../distributed-systems/processing/spark.md) operations distributed across the cluster:

```python
from pyspark.sql import functions as F

# Load from Delta Lake table
df = spark.table("silver.documents")

# Transform
df_clean = (df
    .filter(F.col("language") == "ar")
    .withColumn("word_count", F.size(F.split(F.col("content"), " ")))
    .groupBy("department")
    .agg(F.count("*").alias("doc_count"), F.avg("word_count").alias("avg_words"))
)

# Write to Gold layer
df_clean.write.format("delta").mode("overwrite").saveAsTable("gold.department_stats")
```

Key difference from pandas: [Spark](../../distributed-systems/processing/spark.md) DataFrames are lazy (operations build a query plan, `.write` or `.show()` triggers execution) and distributed (the cluster splits the data across nodes automatically).

## Databricks vs Self-Hosted Spark vs Alternatives

| | Databricks | Self-managed [Spark](../../distributed-systems/processing/spark.md) (EMR, Dataproc) | Traditional [SQL](../../databases/relational/sql.md) DW (Snowflake, BigQuery) |
|---|---|---|---|
| Setup | Managed, no infra | You manage the cluster | Fully managed |
| [Delta Lake](delta-lake.md) | Built-in | Bring your own | Proprietary formats |
| ML / MLflow | First-class | Add separately | Not native |
| [SQL](../../databases/relational/sql.md) analytics | Yes (Databricks [SQL](../../databases/relational/sql.md)) | Limited | Primary use case |
| Cost model | DBU (Databricks Units) + cloud compute | Cloud compute only | Query-based pricing |
| Best for | Data engineering + ML together | Cost-optimized [Spark](../../distributed-systems/processing/spark.md) | Pure [SQL](../../databases/relational/sql.md) analytics |

## In an Enterprise RAG Context

Databricks is upstream of the [RAG](../../ai/rag/rag.md) retrieval layer — it prepares and curates documents before they reach the vector store:

```
Source systems (SharePoint, databases, file shares)
    ↓
Databricks (ingest, clean, chunk, enrich metadata)
    ↓
Azure AI Search / pgvector (indexed for retrieval)
    ↓
RAG pipeline (retrieve → generate)
```

A Databricks pipeline might: extract text from PDFs with [Docling](../../ai/ingestion/docling.md), chunk documents, generate [embeddings](../../ai/ingestion/embeddings.md), and write the resulting records to a Delta table that feeds the vector store indexer.

## Related
- [ADLS](../azure/adls.md) — the cloud storage Databricks reads from and writes to on [Azure](../azure/azure.md)
- [Spark](../../distributed-systems/processing/spark.md) — the processing engine Databricks is built around running
- [Azure Synapse](../azure/azure-synapse.md) — the overlapping Microsoft-native alternative
- [Medallion Architecture](medallion-architecture.md) — the Bronze/Silver/Gold pattern Databricks notebooks/jobs typically implement
- [Delta Lake](delta-lake.md) — the table format Databricks originated and is built tightly around
- [Hadoop vs. Spark vs. Databricks vs. Synapse vs. ADLS/S3/GCS](../../../overviews/cloud/hadoop-spark-databricks-synapse-storage.md) — the full layered picture
- [Governed Data](governed-data.md) — Unity Catalog is the governance layer; what "governed" means in practice
- [Azure AI Foundry](../azure/azure-ai-foundry.md)
- [Document Indexing](../../ai/ingestion/document-indexing.md)
- [Embeddings](../../ai/ingestion/embeddings.md)
- [Pipeline Orchestration](../../ai/infrastructure/pipeline-orchestration.md)
