#!/bin/bash
# DataPulse full end-to-end demo (Linux/macOS/WSL). For Windows, run the
# equivalent commands manually (see README.md "Local Setup").
set -e

echo "=== Checking Docker ==="
docker version > /dev/null

echo "=== Starting all core services ==="
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build \
  postgres minio backend adminer kafka kafka-init kafka-ui \
  prometheus grafana kafka-exporter marquez-db marquez marquez-web frontend

echo "=== Waiting for services to settle ==="
sleep 15

echo "=== Applying schemas ==="
cat infrastructure/postgres/schema/watermarks_schema.sql | docker exec -i datapulse-postgres psql -U datapulse -d datapulse_source
docker exec -it datapulse-postgres psql -U datapulse -d postgres -c "CREATE DATABASE datapulse_test;" || true
docker exec -it datapulse-postgres psql -U datapulse -d postgres -c "CREATE DATABASE datapulse_warehouse;" || true
cat infrastructure/postgres_warehouse/schema/warehouse_schemas.sql | docker exec -i datapulse-postgres psql -U datapulse -d datapulse_warehouse

echo "=== Running backend migrations ==="
docker compose exec -T backend alembic upgrade head || true

echo "=== Generating synthetic data ==="
python scripts/generate_data.py --customers 500 --products 50 --orders 2000 --events 6000 --seed 42 --reset

echo "=== Registering demo tenant 'acme' ==="
curl -s -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" \
  -d '{"tenant_slug":"acme","tenant_name":"ACME Corporation","email":"owner@acme.io","password":"supersecret123","full_name":"Alice Owner"}' || true

TOKEN=$(curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
  -d '{"tenant_slug":"acme","email":"owner@acme.io","password":"supersecret123"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

echo "=== Running ingestion ==="
python -m ingestion.cli --tenant acme --api-token "$TOKEN"

echo "=== Running Spark batch (bronze -> silver -> gold) ==="
docker compose --profile batch run --rm spark python jobs/batch/bronze_to_silver.py --tenant acme --api-token "$TOKEN" || echo "Spark batch step failed/skipped — see docs/spark.md"
docker compose --profile batch run --rm spark python jobs/batch/silver_to_gold.py --tenant acme --api-token "$TOKEN" || echo "Spark gold step failed/skipped"

echo "=== Loading warehouse (local Postgres fallback) ==="
WAREHOUSE_BACKEND=postgres_local python -m warehouse.cli --tenant acme || echo "Warehouse load failed/skipped"

echo "=== Running dbt ==="
(cd dbt/datapulse && dbt deps && dbt run --target local && dbt test --target local) || echo "dbt step failed/skipped — see docs/dbt.md"

echo "=== Running data quality checks ==="
python -m data_quality.cli --tenant acme --api-token "$TOKEN" || echo "Data quality step failed/skipped"

echo "=== Starting streaming (60s demo burst) ==="
docker compose --profile streaming up -d --build spark-streaming || true
python -m streaming.cli --tenant acme --rate 10 --duration 30 || echo "Streaming producer failed/skipped"

echo ""
echo "================================================================"
echo " DATAPULSE DEMO READY"
echo "================================================================"
echo "Frontend:        http://localhost:3000"
echo "API / Swagger:   http://localhost:8000/docs"
echo "Airflow:         http://localhost:8080  (admin/admin, if started)"
echo "Kafka UI:        http://localhost:8081"
echo "MinIO Console:   http://localhost:9001  (minioadmin/minioadmin)"
echo "Grafana:         http://localhost:3001  (admin/admin)"
echo "Prometheus:      http://localhost:9090"
echo "Marquez:         http://localhost:3002"
echo "Adminer:         http://localhost:8082"
echo ""
echo "Login: tenant=acme  email=owner@acme.io  password=supersecret123"
echo ""
echo "To stop everything: docker compose down   (add -v to also wipe data)"
