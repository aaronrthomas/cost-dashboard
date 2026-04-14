"""
Database connection and query helpers for AWS cost data.
Provides functions to query aws_resources, aws_costs, and top_cost_resources,
and aggregate results by service type, subscription, or time period.
"""

import psycopg
from psycopg.rows import dict_row
from config import DB_CONFIG
from datetime import date, datetime
from decimal import Decimal


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def get_connection():
    """Create and return a new PostgreSQL connection."""
    return psycopg.connect(**DB_CONFIG)


# ---------------------------------------------------------------------------
# JSON serialisation helper
# ---------------------------------------------------------------------------

def _serialise(obj):
    """Convert non-JSON-serialisable types for json.dumps default kwarg."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} is not JSON serialisable")


# ---------------------------------------------------------------------------
# Raw table queries
# ---------------------------------------------------------------------------

def fetch_aws_resources(conn):
    """Fetch all rows from aws_resources."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT * FROM aws_resources ORDER BY resource_id;")
        return cur.fetchall()


def fetch_aws_costs(conn):
    """Fetch all rows from aws_costs."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT * FROM aws_costs ORDER BY cost_date;")
        return cur.fetchall()


def fetch_top_cost_resources(conn):
    """Fetch all rows from top_cost_resources."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT * FROM top_cost_resources ORDER BY total_cost DESC;")
        return cur.fetchall()


# ---------------------------------------------------------------------------
# Aggregation: by service type
# ---------------------------------------------------------------------------

def aggregate_by_service(conn):
    """
    Group cost data by AWS service type.

    Returns a dict keyed by service name, each containing:
      - total_cost
      - resource_count
      - resources   (list of resource details)
      - cost_entries (list of cost rows for that service)
    """
    query = """
        SELECT
            r.service_type,
            r.resource_id,
            r.resource_name,
            r.region,
            r.subscription_id,
            COALESCE(SUM(c.cost_amount), 0) AS total_cost,
            COUNT(c.cost_id) AS cost_entries
        FROM aws_resources r
        LEFT JOIN aws_costs c ON r.resource_id = c.resource_id
        GROUP BY r.service_type, r.resource_id, r.resource_name,
                 r.region, r.subscription_id
        ORDER BY r.service_type, total_cost DESC;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        rows = cur.fetchall()

    services = {}
    for row in rows:
        svc = row["service_type"]
        if svc not in services:
            services[svc] = {
                "service_type": svc,
                "total_cost": 0,
                "resource_count": 0,
                "resources": [],
            }
        services[svc]["total_cost"] += float(row["total_cost"])
        services[svc]["resource_count"] += 1
        services[svc]["resources"].append({
            "resource_id": row["resource_id"],
            "resource_name": row["resource_name"],
            "region": row["region"],
            "subscription_id": row["subscription_id"],
            "total_cost": float(row["total_cost"]),
            "cost_entries": row["cost_entries"],
        })

    return {
        "grouped_by": "service_type",
        "data": list(services.values()),
    }


# ---------------------------------------------------------------------------
# Aggregation: by subscription
# ---------------------------------------------------------------------------

def aggregate_by_subscription(conn):
    """
    Group cost data by subscription / account.

    Returns a dict keyed by subscription_id, each containing:
      - total_cost
      - services  (breakdown per service type within the subscription)
    """
    query = """
        SELECT
            r.subscription_id,
            r.service_type,
            r.resource_id,
            r.resource_name,
            COALESCE(SUM(c.cost_amount), 0) AS total_cost
        FROM aws_resources r
        LEFT JOIN aws_costs c ON r.resource_id = c.resource_id
        GROUP BY r.subscription_id, r.service_type,
                 r.resource_id, r.resource_name
        ORDER BY r.subscription_id, total_cost DESC;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        rows = cur.fetchall()

    subscriptions = {}
    for row in rows:
        sub_id = row["subscription_id"]
        if sub_id not in subscriptions:
            subscriptions[sub_id] = {
                "subscription_id": sub_id,
                "total_cost": 0,
                "services": {},
            }
        svc = row["service_type"]
        if svc not in subscriptions[sub_id]["services"]:
            subscriptions[sub_id]["services"][svc] = {
                "service_type": svc,
                "total_cost": 0,
                "resources": [],
            }

        cost = float(row["total_cost"])
        subscriptions[sub_id]["total_cost"] += cost
        subscriptions[sub_id]["services"][svc]["total_cost"] += cost
        subscriptions[sub_id]["services"][svc]["resources"].append({
            "resource_id": row["resource_id"],
            "resource_name": row["resource_name"],
            "total_cost": cost,
        })

    # Convert nested services dict to list for cleaner JSON
    for sub in subscriptions.values():
        sub["services"] = list(sub["services"].values())

    return {
        "grouped_by": "subscription",
        "data": list(subscriptions.values()),
    }


# ---------------------------------------------------------------------------
# Aggregation: by time period (daily / monthly)
# ---------------------------------------------------------------------------

def aggregate_by_time(conn, period="daily"):
    """
    Group cost data by time period.

    Args:
        period: 'daily' or 'monthly'

    Returns a dict with time-bucketed cost aggregates.
    """
    if period == "monthly":
        date_trunc = "month"
    else:
        date_trunc = "day"

    query = f"""
        SELECT
            date_trunc('{date_trunc}', c.cost_date)  AS period_start,
            r.service_type,
            COALESCE(SUM(c.cost_amount), 0)           AS total_cost,
            COUNT(DISTINCT r.resource_id)              AS resource_count
        FROM aws_costs c
        JOIN aws_resources r ON r.resource_id = c.resource_id
        GROUP BY period_start, r.service_type
        ORDER BY period_start, total_cost DESC;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        rows = cur.fetchall()

    periods = {}
    for row in rows:
        key = row["period_start"].isoformat()
        if key not in periods:
            periods[key] = {
                "period_start": key,
                "total_cost": 0,
                "services": [],
            }
        cost = float(row["total_cost"])
        periods[key]["total_cost"] += cost
        periods[key]["services"].append({
            "service_type": row["service_type"],
            "total_cost": cost,
            "resource_count": row["resource_count"],
        })

    return {
        "grouped_by": f"time_{period}",
        "period_type": period,
        "data": list(periods.values()),
    }


# ---------------------------------------------------------------------------
# Combined dashboard payload
# ---------------------------------------------------------------------------

def get_dashboard_data(conn):
    """
    Build a single JSON-ready payload combining every aggregation
    plus the raw top-cost resources list — ideal for a dashboard frontend.
    """
    return {
        "by_service": aggregate_by_service(conn),
        "by_subscription": aggregate_by_subscription(conn),
        "by_day": aggregate_by_time(conn, period="daily"),
        "by_month": aggregate_by_time(conn, period="monthly"),
        "top_cost_resources": [dict(r) for r in fetch_top_cost_resources(conn)],
    }
