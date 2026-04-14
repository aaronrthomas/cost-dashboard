# AWS Cost Dashboard Integrator

## 📌 Overview
The **AWS Cost Dashboard Integrator** is a backend utility that aggregates AWS resource and cost data stored in a PostgreSQL database and exposes it in a structured JSON format suitable for frontend dashboards.

The project demonstrates:
- Database querying and joins
- Cost aggregation logic
- Backend-to-frontend data contracts
- JSON-based API design

This solution supports both:
- JSON file generation
- REST API exposure using Flask

---

## 🎯 Objectives
- Query multiple PostgreSQL tables (`aws_resources`, `aws_costs`, `top_cost_resources`)
- Aggregate AWS cost data by service, subscription, and time
- Generate frontend-friendly structured JSON
- Provide the data via an API or static JSON file

---

## 🛠 Tech Stack
- **Python 3.9+**
- **PostgreSQL**
- **psycopg (v3)**
- **Flask**
- **python-dotenv**

---

## 📂 Project Structure
```text
├── Screenshots/                # Project screenshots
├── README.md                   # Project documentation
├── app.py                      # Core data aggregation & JSON generator
├── db.py                       # Database connection & query helpers
├── config.py                   # Loads DB settings from .env
├── generate_json.py            # CLI script to export individual JSON files
├── seed_db.py                  # Creates tables & inserts sample data
├── cost_dashboard.json         # Generated combined JSON output
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── output/                     # Individual aggregation JSON files
    ├── by_service.json
    ├── by_subscription.json
    └── by_day.json
```

---

## 🗄 Database Schema Assumptions

### aws_resources
| Column          | Type    | Description                       |
|-----------------|---------|-----------------------------------|
| resource_id     | SERIAL  | Unique AWS resource ID            |
| resource_name   | VARCHAR | Human-readable resource name      |
| service_type    | VARCHAR | AWS service (EC2, S3, RDS, etc.)  |
| region          | VARCHAR | AWS region                        |
| subscription_id | VARCHAR | AWS subscription/account          |
| created_at      | TIMESTAMP | Resource creation timestamp     |

### aws_costs
| Column      | Type    | Description              |
|-------------|---------|--------------------------|
| cost_id     | SERIAL  | Primary key              |
| resource_id | INTEGER | Linked resource ID (FK)  |
| cost_date   | DATE    | Date of usage            |
| cost_amount | NUMERIC | Cost incurred            |
| currency    | VARCHAR | Currency code (default: USD) |

### top_cost_resources
| Column        | Type    | Description                |
|---------------|---------|----------------------------|
| id            | SERIAL  | Primary key                |
| resource_id   | INTEGER | Resource ID (FK)           |
| resource_name | VARCHAR | Human-readable name        |
| service_type  | VARCHAR | AWS service type           |
| total_cost    | NUMERIC | Aggregated total cost      |
| rank          | INTEGER | Cost ranking               |

> ⚠️ Note: If your schema differs, adjust SQL queries in `db.py` accordingly.

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/aaronrthomas/cost-dashboard.git
cd cost-dashboard
```

### 2️⃣ Create Virtual Environment (Recommended)
```bash
python -m venv venv
```
Activate:
- **Windows:**
```bash
venv\Scripts\activate
```
- **Linux/Mac:**
```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Database Connection
Copy the example env file and edit it with your PostgreSQL credentials:
```bash
cp .env.example .env
```
Edit `.env` with your actual values:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aws_cost_db
DB_USER=postgres
DB_PASSWORD=your_password
```
Ensure PostgreSQL is running.

### 5️⃣ Seed Sample Data (Optional)
If you want to test with pre-built sample data:
```bash
python seed_db.py
```
This creates the three tables and inserts realistic cost entries.

---

## ▶️ Running the Project

### Option 1: Generate Combined JSON File
```bash
python app.py
```
Output:
```
[OK] cost_dashboard.json generated successfully
```
This reads the aggregated data from `output/` and produces a single `cost_dashboard.json` file.

### Option 2: Generate Individual JSON Files
```bash
python generate_json.py                      # all aggregations
python generate_json.py --group service      # only by_service.json
python generate_json.py --group subscription # only by_subscription.json
python generate_json.py --group daily        # only by_day.json
python generate_json.py --group monthly      # only by_month.json
python generate_json.py --group dashboard    # combined dashboard.json
```
Output files are written to `output/`.

---

## 📊 JSON Output Structure

The generated `cost_dashboard.json` contains:

```json
{
  "generated_at": "2026-04-14T12:27:32.143026+00:00",
  "by_service": {
    "grouped_by": "service_type",
    "data": [
      {
        "service_type": "EC2",
        "total_cost": 93.6,
        "resource_count": 2,
        "resources": [...]
      }
    ]
  },
  "by_subscription": {
    "grouped_by": "subscription",
    "data": [...]
  },
  "by_day": {
    "grouped_by": "time_daily",
    "period_type": "daily",
    "data": [...]
  }
}
```

---

## 🖼 Key Screenshots

### app.py — Core Data Aggregation Script
![58b80ed1-dfc6-446a-b1f0-be29c601c23a](https://github.com/user-attachments/assets/1f51a759-4337-4a0e-9e16-47e119172670)


---

### Generated JSON Output — cost_dashboard.json
![3b4ac9a2-ecde-4a39-832d-976f1c7e383e](https://github.com/user-attachments/assets/075a36ae-9649-49bf-b122-7517a6549f91)


---

### PostgreSQL Tables in pgAdmin
![dea26164-6da8-4575-af1f-4ccf490ca6d9](https://github.com/user-attachments/assets/a427efc3-e859-42e8-97c8-14ad662c8224)

---

### Terminal Output — Successful JSON Generation
![2b80050c-3e2c-439a-a2e1-5699f8a7fb14](https://github.com/user-attachments/assets/ff82cce5-08e6-42e5-9367-b8d20d68fe7b)
