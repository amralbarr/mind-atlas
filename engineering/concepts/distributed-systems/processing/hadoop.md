# Apache Hadoop

Hadoop is the original open-source distributed storage-and-processing framework for big data — the project that established the "split data and computation across many cheap machines" pattern [Spark](spark.md) later built on and mostly displaced for new workloads. It's actually two separate pieces bundled under one name: a distributed filesystem (HDFS) and a distributed processing model (MapReduce).

## The two core pieces

| Component | What it does |
|---|---|
| **HDFS (Hadoop Distributed File System)** | Splits large files into blocks, replicates each block across multiple machines, and presents it all as one logical filesystem — the direct ancestor of the "store data across a cluster of commodity machines" idea that [ADLS](../../cloud/azure/adls.md), [S3](../../protocols/s3-api.md), and [GCS](../../cloud/infrastructure/gcs.md) all build on, though none of those three actually run HDFS themselves anymore — they're independent object-storage services that happen to speak Hadoop-compatible protocols for interoperability |
| **MapReduce** | The original distributed processing model: a **Map** step transforms each piece of data independently and in parallel, a shuffle step groups related results together, and a **Reduce** step aggregates them — writing intermediate results to disk between every step |

## Why Spark mostly replaced it

MapReduce's defining weakness is that it writes intermediate results to disk after every Map and Reduce step — correct and fault-tolerant, but slow, especially for iterative workloads (machine learning training, multi-step ETL) that repeat the same computation pattern many times over the same data. [Spark](spark.md) solved this by keeping intermediate data in memory across steps instead, which is the single biggest reason it's commonly cited as 10-100x faster than MapReduce for the same class of job — see [Spark](spark.md) for the full comparison.

## Why it still matters today

Hadoop isn't dead — it's the reason the ecosystem looks the way it does:

- **The `s3a://`/`abfss://`/`gs://` URI schemes** that [S3](../../protocols/s3-api.md), [ADLS](../../cloud/azure/adls.md), and [GCS](../../cloud/infrastructure/gcs.md) all support exist specifically so [Spark](spark.md) (and other tools) can talk to these cloud object stores using Hadoop-compatible filesystem connectors, without the actual storage being HDFS at all.
- Many existing enterprise data platforms still run real on-premises Hadoop clusters (HDFS + YARN as the cluster manager) that haven't migrated to cloud [object storage](../../cloud/infrastructure/object-storage.md).
- **YARN** (Yet Another Resource Negotiator), Hadoop's cluster resource manager, is still a common choice for scheduling [Spark](spark.md) jobs on self-managed clusters, alongside [Kubernetes](../kubernetes/ingress.md) and standalone [Spark](spark.md) scheduling.

## Related

- [Spark](spark.md) — the faster, mostly-replacement processing engine built on the same distributed-cluster idea
- [ADLS](../../cloud/azure/adls.md), [S3](../../protocols/s3-api.md), [GCS](../../cloud/infrastructure/gcs.md) — modern object stores that speak Hadoop-compatible protocols without running HDFS themselves
- [Databricks](../../cloud/data/databricks.md) — a managed [Spark](spark.md) platform, the practical modern alternative to running a self-managed Hadoop cluster
- [Hadoop vs. Spark vs. Databricks vs. Synapse vs. ADLS/S3/GCS](../../../overviews/cloud/hadoop-spark-databricks-synapse-storage.md) — the full layered picture: storage vs. compute engine vs. managed platform
