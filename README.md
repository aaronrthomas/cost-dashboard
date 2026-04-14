# AWS Cost Dashboard — Backend

Python + PostgreSQL backend that queries `aws_resources`, `aws_costs`, and `top_cost_resources`, aggregates data by **service type**, **subscription**, and **time period** (daily/monthly), and exposes it via a Flask REST API or as static JSON files.

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure database

Copy the example env file and edit it with your PostgreSQL credentials:

```bash
cp .env.example .env
# edit .env with your actual DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
```

### 3. Seed sample data (optional)

If you want to test with pre-built sample data:

```bash
python seed_db.py
```

This creates the three tables and inserts realistic cost entries.

### 4a. Run the Flask API

```bash
python app.py
# → Listening on http://0.0.0.0:5000
```

### 4b. Or generate static JSON files

```bash
python generate_json.py              # all aggregations
python generate_json.py --group service       # only by_service.json
python generate_json.py --group subscription  # only by_subscription.json
python generate_json.py --group daily         # only by_day.json
python generate_json.py --group monthly       # only by_month.json
python generate_json.py --group dashboard     # combined dashboard.json
```

Output files are written to `output/`.

---

## API Endpoints

| Method | Path                         | Description                        |
|--------|------------------------------|------------------------------------|
| GET    | `/health`                    | Health check                       |
| GET    | `/api/resources`             | Raw `aws_resources` rows           |
| GET    | `/api/costs`                 | Raw `aws_costs` rows               |
| GET    | `/api/top-cost-resources`    | Raw `top_cost_resources` rows      |
| GET    | `/api/aggregate/service`     | Costs grouped by service type      |
| GET    | `/api/aggregate/subscription`| Costs grouped by subscription      |
| GET    | `/api/aggregate/time`        | Costs grouped by time period       |
|        |                              | Query: `?period=daily` or `monthly`|
| GET    | `/api/dashboard`             | Combined payload for full dashboard|

All responses are JSON with CORS enabled for frontend integration.

---

## JSON Structure Samples

Pre-generated sample outputs are in `output/`:

- `by_service.json` — grouped by AWS service type
- `by_subscription.json` — grouped by subscription/account
- `by_day.json` — daily time-series breakdown

---

## Project Structure

```
devops/
├── .env.example        # Environment variable template
├── requirements.txt    # Python dependencies
├── config.py           # Loads DB settings from .env
├── db.py               # Database queries & aggregation logic
├── app.py              # Flask REST API
├── generate_json.py    # CLI script to export JSON files
├── seed_db.py          # Creates tables + inserts sample data
└── output/             # Generated JSON sample files
    ├── by_service.json
    ├── by_subscription.json
    └── by_day.json
```

## Frontend Integration

### Using the API (recommended)

```javascript
// Fetch all dashboard data in one call
const res = await fetch('http://localhost:5000/api/dashboard');
const data = await res.json();

// data.by_service      → service breakdown
// data.by_subscription → subscription breakdown
// data.by_day          → daily time series
// data.by_month        → monthly time series
// data.top_cost_resources → top spenders
```

### Using static JSON files

If you prefer a static approach, serve the `output/*.json` files and fetch them directly.
