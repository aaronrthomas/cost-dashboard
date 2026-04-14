"""
Standalone script — query PostgreSQL, aggregate data, and write JSON files.

Usage:
    python generate_json.py                      # writes all output files
    python generate_json.py --group service      # only service aggregation
    python generate_json.py --group subscription # only subscription aggregation
    python generate_json.py --group daily        # daily time aggregation
    python generate_json.py --group monthly      # monthly time aggregation
    python generate_json.py --group dashboard    # full combined dashboard
"""

import argparse
import json
import os
from db import (
    get_connection,
    aggregate_by_service,
    aggregate_by_subscription,
    aggregate_by_time,
    get_dashboard_data,
    _serialise,
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def _write(filename: str, data: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=_serialise)
    print(f"  ✓ {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Export AWS cost aggregations as JSON files."
    )
    parser.add_argument(
        "--group",
        choices=["service", "subscription", "daily", "monthly", "dashboard", "all"],
        default="all",
        help="Which aggregation to export (default: all)",
    )
    args = parser.parse_args()

    conn = get_connection()
    try:
        targets = {
            "service":      lambda: _write("by_service.json",      aggregate_by_service(conn)),
            "subscription": lambda: _write("by_subscription.json", aggregate_by_subscription(conn)),
            "daily":        lambda: _write("by_day.json",          aggregate_by_time(conn, "daily")),
            "monthly":      lambda: _write("by_month.json",        aggregate_by_time(conn, "monthly")),
            "dashboard":    lambda: _write("dashboard.json",       get_dashboard_data(conn)),
        }

        if args.group == "all":
            print("Generating all JSON exports…")
            for fn in targets.values():
                fn()
        else:
            print(f"Generating {args.group} export…")
            targets[args.group]()

        print("\nDone.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
