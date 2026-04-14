"""
Bootstrap script — creates the three tables and inserts realistic sample data
so you can test the queries and API without a production database.

Usage:
    python seed_db.py
"""

import psycopg
from config import DB_CONFIG

DDL = """
-- aws_resources: inventory of cloud resources
CREATE TABLE IF NOT EXISTS aws_resources (
    resource_id      SERIAL PRIMARY KEY,
    resource_name    VARCHAR(255) NOT NULL,
    service_type     VARCHAR(100) NOT NULL,
    region           VARCHAR(50)  NOT NULL,
    subscription_id  VARCHAR(100) NOT NULL,
    created_at       TIMESTAMP DEFAULT NOW()
);

-- aws_costs: daily cost entries per resource
CREATE TABLE IF NOT EXISTS aws_costs (
    cost_id       SERIAL PRIMARY KEY,
    resource_id   INTEGER REFERENCES aws_resources(resource_id),
    cost_date     DATE NOT NULL,
    cost_amount   NUMERIC(12, 4) NOT NULL,
    currency      VARCHAR(10) DEFAULT 'USD'
);

-- top_cost_resources: pre-aggregated top spenders (e.g. materialised view)
CREATE TABLE IF NOT EXISTS top_cost_resources (
    id              SERIAL PRIMARY KEY,
    resource_id     INTEGER REFERENCES aws_resources(resource_id),
    resource_name   VARCHAR(255),
    service_type    VARCHAR(100),
    total_cost      NUMERIC(14, 4),
    rank            INTEGER
);
"""

SEED_RESOURCES = """
INSERT INTO aws_resources (resource_name, service_type, region, subscription_id) VALUES
    ('web-prod-1',       'EC2',         'us-east-1', 'sub-001'),
    ('web-prod-2',       'EC2',         'us-east-1', 'sub-001'),
    ('api-gateway-main', 'API Gateway', 'us-east-1', 'sub-001'),
    ('db-primary',       'RDS',         'us-east-1', 'sub-002'),
    ('db-replica',       'RDS',         'us-west-2', 'sub-002'),
    ('data-lake',        'S3',          'us-east-1', 'sub-002'),
    ('cdn-assets',       'CloudFront',  'global',    'sub-001'),
    ('lambda-etl',       'Lambda',      'us-east-1', 'sub-003'),
    ('cache-cluster',    'ElastiCache', 'us-east-1', 'sub-003'),
    ('search-cluster',   'OpenSearch',  'us-west-2', 'sub-003')
ON CONFLICT DO NOTHING;
"""

SEED_COSTS = """
INSERT INTO aws_costs (resource_id, cost_date, cost_amount) VALUES
    -- March 2026 daily samples
    (1, '2026-03-01', 12.50), (1, '2026-03-02', 13.10), (1, '2026-03-03', 11.90),
    (2, '2026-03-01',  9.80), (2, '2026-03-02', 10.20), (2, '2026-03-03', 10.00),
    (3, '2026-03-01',  3.40), (3, '2026-03-02',  3.55), (3, '2026-03-03',  3.30),
    (4, '2026-03-01', 45.00), (4, '2026-03-02', 44.80), (4, '2026-03-03', 46.20),
    (5, '2026-03-01', 22.30), (5, '2026-03-02', 21.90), (5, '2026-03-03', 23.10),
    (6, '2026-03-01',  1.20), (6, '2026-03-02',  1.35), (6, '2026-03-03',  1.10),
    (7, '2026-03-01',  8.00), (7, '2026-03-02',  7.60), (7, '2026-03-03',  8.40),
    (8, '2026-03-01',  0.45), (8, '2026-03-02',  0.52), (8, '2026-03-03',  0.38),
    (9, '2026-03-01', 18.00), (9, '2026-03-02', 17.50), (9, '2026-03-03', 18.60),
    (10,'2026-03-01', 35.00), (10,'2026-03-02', 34.20), (10,'2026-03-03', 36.10),
    -- April 2026 daily samples
    (1, '2026-04-01', 12.80), (1, '2026-04-02', 13.30),
    (4, '2026-04-01', 47.50), (4, '2026-04-02', 46.90),
    (7, '2026-04-01',  8.20), (7, '2026-04-02',  7.90),
    (10,'2026-04-01', 37.00), (10,'2026-04-02', 35.80);
"""

SEED_TOP_COST = """
INSERT INTO top_cost_resources (resource_id, resource_name, service_type, total_cost, rank) VALUES
    (4,  'db-primary',      'RDS',         230.40, 1),
    (10, 'search-cluster',  'OpenSearch',  178.10, 2),
    (1,  'web-prod-1',       'EC2',          63.60, 3),
    (9,  'cache-cluster',    'ElastiCache',  54.10, 4),
    (5,  'db-replica',       'RDS',          67.30, 5)
ON CONFLICT DO NOTHING;
"""


def main():
    conn = psycopg.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    print("Creating tables…")
    cur.execute(DDL)

    print("Inserting sample data…")
    cur.execute(SEED_RESOURCES)
    cur.execute(SEED_COSTS)
    cur.execute(SEED_TOP_COST)

    print("Done — sample database is ready.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
