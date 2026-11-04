# Azure Synapse Analytics

Azure Synapse Analytics is Microsoft's unified big-data and data-warehousing platform — it combines [SQL](../../databases/relational/sql.md)-based data warehousing, [Spark](../../distributed-systems/processing/spark.md)-based big-data processing, and [pipeline orchestration](../../ai/infrastructure/pipeline-orchestration.md) under one workspace, reading and writing data that typically lives in [ADLS](adls.md). Where [Databricks](../data/databricks.md) is the [Spark](../../distributed-systems/processing/spark.md)-first lakehouse platform, Synapse is Microsoft's own [SQL](../../databases/relational/sql.md)-first-and-[Spark](../../distributed-systems/processing/spark.md)-second answer to the same "analyze data stored in the lake" problem — the two overlap significantly and a given organization typically standardizes on one rather than running both.

## Core components

| Component | What it does |
|---|---|
| **Synapse [SQL](../../databases/relational/sql.md) (dedicated / serverless pools)** | A [SQL](../../databases/relational/sql.md) data warehouse engine for querying structured data at scale — dedicated pools are pre-provisioned capacity (predictable cost, always-on), serverless pools are pay-per-query (no provisioning, cheaper for sporadic workloads) |
| **Synapse [Spark](../../distributed-systems/processing/spark.md) pools** | Managed [Apache Spark](../../distributed-systems/processing/spark.md) clusters for big-data processing, the same workload class [Databricks](../data/databricks.md) targets |
| **Synapse Pipelines** | Data integration/orchestration — functionally the same role as the standalone [Azure Data Factory](azure-data-factory.md) service, since Synapse Pipelines is built on the same underlying engine |
| **Synapse Studio** | The unified web workspace — notebooks, [SQL](../../databases/relational/sql.md) scripts, pipeline design, and monitoring in one UI |

## Where it fits relative to ADLS and Databricks

```
ADLS (raw storage)
    ↓
Synapse Spark pools  OR  Databricks   ← transformation/processing (pick one ecosystem)
    ↓
Synapse SQL pools                     ← serve curated data to BI tools / applications
```

Synapse [SQL](../../databases/relational/sql.md) pools are the piece without a direct [Databricks](../data/databricks.md) equivalent in this comparison — [Databricks](../data/databricks.md) is primarily a processing/[Spark](../../distributed-systems/processing/spark.md) platform, while Synapse bundles processing *and* a [SQL](../../databases/relational/sql.md) serving layer together. A team already standardized on [Databricks](../data/databricks.md) for processing would typically still need a separate SQL warehouse ([Databricks](../data/databricks.md) SQL, or another warehouse product) to serve the same "query curated data via SQL" role Synapse SQL pools provide natively.

## Related

- [ADLS](adls.md) — the storage layer both Synapse [Spark](../../distributed-systems/processing/spark.md) and Synapse SQL read from
- [Spark](../../distributed-systems/processing/spark.md) — the engine behind Synapse [Spark](../../distributed-systems/processing/spark.md) pools
- [Databricks](../data/databricks.md) — the overlapping Spark-first alternative
- [Azure Data Factory](azure-data-factory.md) — the standalone orchestration service Synapse Pipelines is built on
- [Hadoop vs. Spark vs. Databricks vs. Synapse vs. ADLS/S3/GCS](../../../overviews/cloud/hadoop-spark-databricks-synapse-storage.md) — the full layered picture, including where Synapse fits relative to Microsoft Fabric
- [Azure AI Foundry](azure-ai-foundry.md)
