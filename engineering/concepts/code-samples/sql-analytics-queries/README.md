# SQL Analytics Queries — Runnable Example

The exact multi-tenant revenue-aggregation query from
[the SQL exercise](../../interview/interview-01/08-sql-analytics-ml.md#sql-exercise-calculate-revenue-without-duplicating-orders),
running against a real seeded [SQLite](../../databases/relational/sqlite.md) database (`sqlite3`, zero external
dependencies) instead of sitting as an inert code block in a markdown file.

Also demonstrates the join-then-aggregate pattern the handbook warns about:
aggregating `order_items` to the order grain *before* joining to `orders`,
so an order's `net_amount` is never duplicated once per item row.

## Run it

```bash
cd code-samples
python3 -m venv .venv
.venv/bin/pip install -r sql-analytics-queries/requirements.txt
.venv/bin/python3 sql-analytics-queries/sql_analytics.py
.venv/bin/pytest sql-analytics-queries/tests/ -v
```

## Concepts this demonstrates

- [SQL](../../databases/relational/sql.md)
- [Multi-Tenancy & Tenant Isolation](../../backend/architecture/multi-tenancy.md) — the `tenant_id` scoping in `REVENUE_QUERY`

## Related

- [Structured Data, Analytics & ML — Interview Q&A](../../interview/interview-01/08-sql-analytics-ml.md)
