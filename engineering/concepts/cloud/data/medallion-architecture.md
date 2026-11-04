# Medallion Architecture (Bronze / Silver / Gold)

The medallion architecture is a data-organization pattern for a data lake — progressively refining raw data through three named layers, each with a clear quality/trust contract, rather than treating "the data lake" as one undifferentiated pile of files. It's the standard way [Databricks](databricks.md) and [Delta Lake](delta-lake.md) workloads structure data stored in [ADLS](../azure/adls.md), S3, or [GCS](../infrastructure/gcs.md), and it's exactly what [ADLS](../azure/adls.md)'s own "Medallion Layers on [ADLS](../azure/adls.md)" example is describing.

## The three layers

```
Bronze  →  Silver  →  Gold
raw        cleaned     business-ready
```

| Layer | Contains | Typical transformations applied to reach it |
|---|---|---|
| **Bronze** | Raw ingested data, as close to the original source format as possible | Minimal — often just landing the file and attaching ingestion metadata (source, timestamp) |
| **Silver** | Validated, cleaned, deduplicated, schema-conformed data | Parsing, type casting, deduplication, join-ability fixes, chunking/metadata-enrichment for document pipelines |
| **Gold** | Business-ready, aggregated, or application-ready data | Business logic, aggregation, feature engineering — or, in a [RAG](../../ai/rag/rag.md) pipeline, embedding vectors ready for indexing |

[ADLS](../azure/adls.md)'s own example of this maps directly onto a document-ingestion pipeline:

```
adls://raw/bronze/documents/          ← raw ingested PDFs / JSON
adls://processed/silver/documents/    ← cleaned, chunked, metadata-enriched
adls://curated/gold/embeddings/       ← embedding vectors ready for indexing
```

## Why this pattern, specifically

- **Reprocessing without re-ingestion.** If a transformation bug is found in the Silver layer's logic, Bronze still has the untouched original data to re-run the fix against — nothing was lost or mutated in place.
- **Clear ownership and trust boundaries.** A consumer reading from Gold can trust the data has already been validated and conformed; a consumer reading from Bronze knows explicitly that it hasn't been.
- **Incremental processing.** Each layer's transformation can run independently and incrementally (new Bronze files trigger a Silver job, new Silver records trigger a Gold job) rather than reprocessing everything from scratch on every run.

## Delta Lake is what makes each layer reliable

The layers are commonly implemented as [Delta Lake](delta-lake.md) tables rather than plain files — [Delta Lake](delta-lake.md) adds [ACID](../../databases/relational/acid.md) transactions, schema enforcement, and time-travel (querying a table as of a previous version) on top of [object storage](../infrastructure/object-storage.md) like [ADLS](../azure/adls.md), which is what makes "update Silver without corrupting it mid-write" or "roll back a bad Gold refresh" actually safe operations rather than manual file-juggling.

## What it does *not* guarantee

The medallion pattern organizes *where* data lives by trust level — it does not itself guarantee correctness, [authorization](../../security/authorization/authorization.md), or governance. A Gold-layer table still needs real data-quality checks, explicit ownership, and [access control](../../ai/retrieval/vector-database.md#metadata-filtering) applied at each layer; "it's in Gold" is not proof the data is correct, current, or that the consuming application is authorized to read it. See [Governed Data](governed-data.md) for what "governed" actually requires beyond just organizing files into layers.

## Related

- [Databricks](databricks.md) — the platform most commonly used to run the Bronze→Silver→Gold transformation jobs
- [Delta Lake](delta-lake.md) — the storage format that gives each layer [ACID](../../databases/relational/acid.md) guarantees
- [ADLS](../azure/adls.md) — the storage layer the medallion layers physically live on
- [Governed Data](governed-data.md) — what correctness/ownership/access-control guarantees the medallion pattern does *not* provide on its own
