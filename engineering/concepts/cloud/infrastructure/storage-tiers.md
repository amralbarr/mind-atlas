# Cloud Storage Tiers

Every major cloud object-storage service offers the same underlying trade-off under different names: cheaper storage in exchange for slower or more expensive access. Picking the right tier for data that's accessed constantly vs. data kept only for compliance is a real cost lever, not a minor detail — the price difference between the cheapest and most expensive tier is commonly 10-20x per GB.

## The shared pattern, across providers

| Tier concept | [ADLS](../azure/adls.md) / [Azure](../azure/azure.md) Blob | [S3](../../protocols/s3-api.md) | [GCS](gcs.md) |
|---|---|---|---|
| Frequent access | **Hot** | Standard | Standard |
| Infrequent access | **Cool** | Standard-IA (Infrequent Access) | Nearline |
| Rarely accessed | **Cold** | Glacier Instant Retrieval | Coldline |
| Archival / compliance | **Archive** | Glacier Deep Archive | Archive |

The names differ, but the underlying shape is identical everywhere: as you move down the table, **storage cost per GB drops**, **retrieval cost per GB rises**, and **retrieval latency gets worse** — from milliseconds (hot/standard tiers) to minutes or hours (archive tiers, which may require an explicit "rehydration" request before a file becomes readable again).

## Why this matters for a document pipeline

In an enterprise [RAG](../../ai/rag/rag.md) ingestion pipeline (see the [Architecture Design Exercise](../../../interview/interview-01/06-design.md)), tiering decisions usually follow the data's actual access pattern through the pipeline:

- **Raw ingested documents** (the Bronze layer, in a [medallion architecture](../data/medallion-architecture.md)) are often moved to a cooler tier once processed — they're kept for audit/reprocessing but rarely read again directly.
- **Curated, chunked, embedded content** (the Gold layer) stays in the hot/standard tier, since it's what's actually read on every query.
- **Superseded document versions** are prime candidates for archive tiers — retained for compliance, essentially never read, but prohibitively expensive to delete outright if retention policy requires keeping them.

## The real risk: choosing a cold tier for data that turns out to be needed often

Every provider's pricing model makes a cold/archive tier attractive by its low storage cost, but retrieval cost and latency can erase those savings quickly if access patterns were misjudged — a batch of "rarely accessed" archive-tier data that turns out to be queried daily can end up costing more in retrieval fees than it would have in a hotter tier's storage fees alone. Tiering decisions benefit from the same measure-don't-assume discipline as everything else in this handbook: base the tier on actual observed access frequency, not a one-time guess at ingestion time.

## Related

- [ADLS](../azure/adls.md) — [Azure](../azure/azure.md)'s Hot/Cool/Cold/Archive tiers
- [Amazon S3 API](../../protocols/s3-api.md) — S3's Standard/Standard-IA/Glacier tiers
- [GCS](gcs.md) — [GCS](gcs.md)'s Standard/Nearline/Coldline/Archive tiers
- [Backup and Restore](backup-and-restore.md)
