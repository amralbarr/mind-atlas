# Azure Data Factory

Azure Data Factory (ADF) is Microsoft's managed data-integration and pipeline-orchestration service — it moves and transforms data between sources on a schedule or trigger, most commonly landing data into [ADLS](adls.md) as the first step of a larger analytics pipeline feeding [Databricks](../data/databricks.md) or [Azure Synapse](azure-synapse.md). It's the orchestration layer, not a compute engine itself — ADF pipelines typically call out to [Databricks](../data/databricks.md) notebooks, Synapse [Spark](../../distributed-systems/processing/spark.md) jobs, or [SQL](../../databases/relational/sql.md) procedures to do the actual data processing.

## Core concepts

| Term | Meaning |
|---|---|
| **Pipeline** | A logical grouping of activities that together perform a task (e.g. copy raw files, then trigger a [Databricks](../data/databricks.md) notebook) |
| **Activity** | A single step inside a pipeline — a Copy activity, a [Databricks](../data/databricks.md) Notebook activity, a stored-procedure call, etc. |
| **Linked Service** | A connection definition to an external system (a storage account, a database, an API) — the credentials/connection string live here, referenced by activities |
| **Dataset** | A named reference to a specific piece of data within a Linked Service (a specific container/path in [ADLS](adls.md), a specific table in a database) |
| **Trigger** | What starts a pipeline run — a schedule, a tumbling window, or an event (e.g. a new file landing in [ADLS](adls.md)) |
| **Integration Runtime** | The compute infrastructure that actually executes activities — [Azure](azure.md)-hosted by default, or a self-hosted IR when the pipeline needs to reach an on-premises/private-network data source |

## A typical document-ingestion pipeline shape

```
Trigger: new file lands in ADLS raw/ container
    ↓
Copy Activity: validate and move to a staging path
    ↓
Databricks Notebook Activity: parse, chunk, embed
    ↓
Copy Activity: write curated output to ADLS gold/ container
```

This is the same ingestion-pipeline role [Databricks Workflows](../data/databricks.md) or a plain cron/[Airflow](../../ai/infrastructure/airflow.md) job plays in a non-[Azure](azure.md) stack — ADF's distinguishing feature is its large library of pre-built connectors to other systems (SaaS APIs, on-premises databases via self-hosted IR, other clouds' storage) without writing custom integration code for each one.

## Related

- [ADLS](adls.md) — the most common source and destination for ADF pipeline activities
- [Databricks](../data/databricks.md) — frequently the actual compute ADF triggers for a pipeline's transformation step
- [Azure Synapse](azure-synapse.md) — Synapse Pipelines is built on the same underlying engine as standalone ADF
