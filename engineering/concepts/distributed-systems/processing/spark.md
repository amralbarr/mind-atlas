# Apache Spark

Apache Spark is a distributed data-processing engine for big-data workloads — the thing that actually runs when [Databricks](../../cloud/data/databricks.md) or [Azure Synapse](../../cloud/azure/azure-synapse.md) "processes" data at scale. It reads from [object storage](../../cloud/infrastructure/object-storage.md) ([ADLS](../../cloud/azure/adls.md), [S3](../../protocols/s3-api.md), [GCS](../../cloud/infrastructure/gcs.md)), transforms data in parallel across a cluster of machines, and writes results back out — the modern, much faster successor to plain [Hadoop MapReduce](hadoop.md) for the same class of problem.

## Why it exists — the problem it solves

A single machine can't process a dataset too large to fit in its memory or too slow to process sequentially in reasonable time. Spark splits both the data and the computation across many machines (a cluster), running the same operations on different chunks of data in parallel, then combining the results — the same "divide the work across many workers" idea [Hadoop](hadoop.md) pioneered, but with a critical difference: Spark keeps intermediate data **in memory** between processing steps rather than writing to disk after every step, which is the main reason it's commonly 10-100x faster than [Hadoop](hadoop.md) MapReduce for iterative workloads (the kind machine learning and multi-step ETL both are).

## Core concepts

| Term | Meaning |
|---|---|
| **RDD (Resilient Distributed Dataset)** | Spark's original low-level data [abstraction](../../programming/fundamentals/abstraction.md) — an immutable, partitioned collection of data spread across the cluster, with automatic recovery if a partition is lost |
| **DataFrame** | A higher-level, schema-aware [abstraction](../../programming/fundamentals/abstraction.md) on top of RDDs (rows and named columns, like a distributed table) — the API most real Spark code uses today instead of raw RDDs |
| **Driver** | The process that runs your main Spark program, builds the execution plan, and coordinates the cluster |
| **Executor** | A worker process on a cluster node that actually runs tasks and holds data partitions |
| **Cluster manager** | What allocates physical resources to Spark — standalone, YARN, [Kubernetes](../kubernetes/ingress.md), or a managed service's own scheduler (e.g. [Databricks](../../cloud/data/databricks.md)' or Synapse's own cluster management) |
| **Job / Stage / Task** | A Spark job (one action, e.g. `.collect()` or a write) breaks down into stages (separated by data shuffles) which break down into tasks (one task per data partition) |
| **Lazy evaluation** | Transformations (`filter`, `select`, `join`) don't execute immediately — Spark builds up a execution plan and only actually runs it when an action (`.write()`, `.count()`) is called, which lets it optimize the whole plan before running anything |

## A minimal example

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("documents").getOrCreate()

df = spark.read.parquet("abfss://raw@account.dfs.core.windows.net/documents/")

chunked = (
    df.filter(df.department == "HR")
      .withColumn("word_count", f.size(f.split(df.text, " ")))
)

chunked.write.mode("overwrite").parquet("abfss://processed@account.dfs.core.windows.net/chunks/")
```

Nothing actually runs until `.write()` is called — the `filter` and `withColumn` calls just build up the plan.

## Where it shows up in this handbook

Spark is the processing engine behind [Databricks](../../cloud/data/databricks.md) notebooks/jobs, [Azure Synapse](../../cloud/azure/azure-synapse.md)'s Spark pools, and the [Delta Lake](../../cloud/data/delta-lake.md) [medallion architecture](../../cloud/data/medallion-architecture.md) (Bronze/Silver/Gold layers) described in [ADLS](../../cloud/azure/adls.md) — in each case, "run a Spark job" is what actually parses, chunks, or transforms raw documents at scale before they reach a vector index.

## Related

- [Hadoop](hadoop.md) — the older, disk-based distributed-processing system Spark displaced for most new workloads
- [Databricks](../../cloud/data/databricks.md) — a managed platform built around running Spark
- [Azure Synapse](../../cloud/azure/azure-synapse.md) — Microsoft's own managed Spark pools
- [ADLS](../../cloud/azure/adls.md) / [S3](../../protocols/s3-api.md) / [GCS](../../cloud/infrastructure/gcs.md) — the [object storage](../../cloud/infrastructure/object-storage.md) Spark jobs typically read from and write to
- [Hadoop vs. Spark vs. Databricks vs. Synapse vs. ADLS/S3/GCS](../../../overviews/cloud/hadoop-spark-databricks-synapse-storage.md) — the full layered picture, with a worked [RAG](../../ai/rag/rag.md)-pipeline example
