# Delta Lake

Delta Lake is an open-source storage format and transaction layer that sits on top of [object storage](../infrastructure/object-storage.md) — [ADLS](../azure/adls.md), S3, or [GCS](../infrastructure/gcs.md) — adding database-like reliability guarantees ([ACID](../../databases/relational/acid.md) transactions, schema enforcement, time travel) to what would otherwise just be a folder of Parquet files. It's the storage format underneath most real-world [medallion architecture](medallion-architecture.md) implementations, and the default table format in [Databricks](databricks.md).

## The problem it solves

Plain files in [object storage](../infrastructure/object-storage.md) have no transactional guarantees: a write can fail halfway through and leave a directory of Parquet files in a partially-written, inconsistent state; two concurrent writers can corrupt each other's output; there's no way to safely add a column without breaking every reader expecting the old schema; and once a bad write happens, there's no built-in way to see or recover the data as it was before. Delta Lake adds a transaction log on top of the raw files that solves all of these.

## Core concepts

| Term | Meaning |
|---|---|
| **Transaction log (`_delta_log`)** | A folder of [JSON](../../programming/fundamentals/json.md) files recording every change ever made to the table — what makes [ACID](../../databases/relational/acid.md) transactions possible on top of plain [object storage](../infrastructure/object-storage.md) |
| **[ACID](../../databases/relational/acid.md) transactions** | Writes either fully succeed or fully fail — no reader ever sees a half-written state, even with multiple concurrent writers |
| **Schema enforcement** | Writes that don't match the table's expected schema are rejected by default, rather than silently corrupting downstream readers |
| **Schema evolution** | Adding a new column (when explicitly allowed) without breaking existing readers of the old schema |
| **Time travel** | Querying the table as it existed at a previous version or timestamp — `SELECT * FROM table VERSION AS OF 12` — using the transaction log's full history |
| **`MERGE` / upserts** | Real insert-or-update operations against a lake table, which plain Parquet files on [object storage](../infrastructure/object-storage.md) can't do natively (an update normally means rewriting whole files) |

## Why it matters for a medallion pipeline specifically

Each layer in a [medallion architecture](medallion-architecture.md) (Bronze/Silver/Gold) is typically a Delta table rather than a plain Parquet directory, specifically because:

- A Silver-layer transformation job can safely re-run without risk of leaving the table half-updated if it fails partway through.
- Deduplication and upserts (a document updated in place, rather than only ever appended) are real operations instead of manual file rewrites.
- Time travel lets you investigate "what did Gold look like before yesterday's bad refresh" directly, without a separate backup process.

## Related

- [Medallion Architecture](medallion-architecture.md) — the data-organization pattern Delta Lake tables typically implement
- [Databricks](databricks.md) — the platform Delta Lake originated from and is most tightly integrated with
- [ADLS](../azure/adls.md) — the [object storage](../infrastructure/object-storage.md) Delta tables are physically stored on
