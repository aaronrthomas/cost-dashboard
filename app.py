"""
Cost Dashboard Integrator — reads pre-generated JSON aggregation files
and combines them into a single cost_dashboard.json output.

Usage:
    python app.py
"""

import json
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

SOURCE_FILES = {
    "by_service":      os.path.join(OUTPUT_DIR, "by_service.json"),
    "by_subscription": os.path.join(OUTPUT_DIR, "by_subscription.json"),
    "by_day":          os.path.join(OUTPUT_DIR, "by_day.json"),
}


def _load_json(filepath):
    """Load and return parsed JSON from a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    # Load each aggregation from the output directory
    dashboard = {
        "submitted_by": "aaronrthomas@mulearn",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        
    }

    for key, path in SOURCE_FILES.items():
        if os.path.exists(path):
            dashboard[key] = _load_json(path)
        else:
            print(f"  ⚠ {os.path.basename(path)} not found, skipping.")
            dashboard[key] = None

    # Write the combined dashboard JSON
    out_path = os.path.join(SCRIPT_DIR, "cost_dashboard.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2)

    print("[OK] cost_dashboard.json generated successfully")


if __name__ == "__main__":
    main()
