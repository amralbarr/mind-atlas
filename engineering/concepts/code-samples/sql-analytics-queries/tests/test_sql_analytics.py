"""Verifies the revenue query correctly excludes refunded/pending orders
and other tenants' orders, and that the join-then-aggregate pattern
doesn't duplicate an order's total across its item rows.

See: ../../../interview/interview-01/08-sql-analytics-ml.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sql_analytics import build_demo_db, order_with_computed_total, paid_revenue  # noqa: E402


def test_revenue_excludes_refunded_and_pending():
    conn = build_demo_db()
    revenue = paid_revenue(conn, tenant_id=100, start_utc="2026-10-01T00:00:00", end_utc="2026-11-01T00:00:00")
    assert revenue == 450.0  # only the two 'paid' orders: 150 + 300


def test_revenue_is_scoped_to_tenant():
    conn = build_demo_db()
    revenue = paid_revenue(conn, tenant_id=200, start_utc="2026-10-01T00:00:00", end_utc="2026-11-01T00:00:00")
    assert revenue == 999.0  # tenant 200's own paid order only


def test_revenue_outside_interval_is_zero():
    conn = build_demo_db()
    revenue = paid_revenue(conn, tenant_id=100, start_utc="2026-01-01T00:00:00", end_utc="2026-02-01T00:00:00")
    assert revenue == 0.0


def test_item_total_matches_order_net_amount_not_duplicated():
    conn = build_demo_db()
    order_id, net_amount, computed_total = order_with_computed_total(conn, order_id=1)
    assert computed_total == net_amount == 150.0
