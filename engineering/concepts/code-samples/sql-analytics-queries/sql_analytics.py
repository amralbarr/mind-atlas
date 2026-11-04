"""Real, runnable SQL against a seeded SQLite database — the exact
multi-tenant revenue-aggregation query from the handbook's SQL exercise,
plus the N+1-avoiding join-then-aggregate pattern it warns about.

Companion to:
- ../../interview/interview-01/08-sql-analytics-ml.md
- ../../concepts/databases/relational/sql.md
- ../../concepts/backend/architecture/multi-tenancy.md
"""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    paid_at TEXT,          -- UTC ISO timestamp, NULL if not yet paid
    status TEXT NOT NULL,  -- 'paid' | 'pending' | 'refunded'
    currency TEXT NOT NULL,
    net_amount REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    sku TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
"""

SEED_ORDERS = [
    # id, tenant_id, paid_at,              status,      currency, net_amount
    (1, 100, "2026-10-01T10:00:00", "paid", "SAR", 150.0),
    (2, 100, "2026-10-05T12:00:00", "paid", "SAR", 300.0),
    (3, 100, "2026-10-10T09:00:00", "refunded", "SAR", 80.0),
    (4, 100, None, "pending", "SAR", 60.0),
    (5, 200, "2026-10-03T11:00:00", "paid", "SAR", 999.0),  # a different tenant
]

SEED_ITEMS = [
    # id, order_id, sku, quantity, unit_price
    (1, 1, "SKU-A", 2, 50.0),
    (2, 1, "SKU-B", 1, 50.0),
    (3, 2, "SKU-A", 3, 100.0),
]


def build_demo_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", SEED_ORDERS)
    conn.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", SEED_ITEMS)
    conn.commit()
    return conn


# The exact exercise query from the handbook: paid SAR revenue for a tenant
# over an explicit UTC interval — status/currency filtered, no joins needed
# since `orders` already carries net_amount at the order grain.
REVENUE_QUERY = """
SELECT COALESCE(SUM(net_amount), 0) AS paid_revenue_sar
FROM orders
WHERE tenant_id = :tenant_id
  AND status = 'paid'
  AND currency = 'SAR'
  AND paid_at >= :start_utc
  AND paid_at < :end_utc
"""


def paid_revenue(conn: sqlite3.Connection, tenant_id: int, start_utc: str, end_utc: str) -> float:
    row = conn.execute(
        REVENUE_QUERY, {"tenant_id": tenant_id, "start_utc": start_utc, "end_utc": end_utc}
    ).fetchone()
    return row[0]


# The join-then-aggregate pattern the handbook warns about: aggregate
# order_items to the ORDER grain FIRST (one row per order_id), then join
# to orders — joining orders directly to order_items without this step
# would duplicate each order's net_amount once per item row.
ITEM_TOTAL_QUERY = """
SELECT o.id, o.net_amount, item_totals.computed_total
FROM orders o
JOIN (
    SELECT order_id, SUM(quantity * unit_price) AS computed_total
    FROM order_items
    GROUP BY order_id
) AS item_totals
ON item_totals.order_id = o.id
WHERE o.id = :order_id
"""


def order_with_computed_total(conn: sqlite3.Connection, order_id: int):
    return conn.execute(ITEM_TOTAL_QUERY, {"order_id": order_id}).fetchone()


if __name__ == "__main__":
    conn = build_demo_db()

    revenue = paid_revenue(conn, tenant_id=100, start_utc="2026-10-01T00:00:00", end_utc="2026-11-01T00:00:00")
    print(f"Tenant 100 paid SAR revenue for October 2026: {revenue}")
    # Expected: 150.0 + 300.0 = 450.0 — the refunded and pending orders are
    # correctly excluded, and tenant 200's order never enters the sum.

    order_id, net_amount, computed_total = order_with_computed_total(conn, order_id=1)
    print(f"Order {order_id}: net_amount={net_amount}, item total={computed_total}")
