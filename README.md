<div align="center">

# DataPulse

### Multi-Tenant Real-Time Data Engineering Platform

*Batch + streaming pipelines · medallion data lake · dimensional warehouse · orchestration · data quality · lineage · monitoring — built in 20 documented phases*

[![CI](https://github.com/YOUR_USERNAME/datapulse/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/datapulse/actions/workflows/ci.yml)
[![Docker Build](https://github.com/YOUR_USERNAME/datapulse/actions/workflows/docker.yml/badge.svg)](https://github.com/YOUR_USERNAME/datapulse/actions/workflows/docker.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org/)
[![dbt](https://img.shields.io/badge/dbt-1.8-orange.svg)](https://www.getdbt.com/)

[Overview](#overview) · [Screenshots](#screenshots) · [Architecture](#architecture) · [Tech Stack](#tech-stack) · [Quick Start](#quick-start) · [Documentation](#documentation)

</div>

---

## Overview

**DataPulse** is a SaaS platform where multiple organizations (tenants) connect
e-commerce data sources and monitor their data pipelines — through both
**batch** and **real-time streaming** paths. It's a complete, production-inspired
data engineering system, not a toy demo: every idempotency guarantee is
tested, every isolation boundary is verified, and every design decision
is documented with the alternatives that were considered and rejected.

Built incrementally across **20 phases**, each one runnable and tested
before moving to the next — from a bare Docker Compose file all the way
to Terraform-provisioned AWS infrastructure with CI/CD.

**What makes this different from a typical portfolio pipeline project:**

- 🔁 **Real idempotency, not just claimed idempotency** — watermarked incremental extraction, Spark's dynamic partition overwrite, and dbt's MERGE-based incremental models are each backed by tests that actually rerun the pipeline and assert no duplication.
- 🔐 **Two independent, composed tenant-isolation layers** — application-layer repository scoping *and* PostgreSQL Row-Level Security — with a documented table of exactly which failure modes each one catches that the other doesn't.
- 📊 **Zero fake dashboard numbers** — every stat card, every metric, every quality score in the frontend is sourced from a real backend endpoint. Where data genuinely isn't available in a JSON API (like Kafka consumer lag), the UI says so and links to Grafana instead of inventing a number.
- 📐 **Honest scope boundaries** — where two subsystems don't fully unify (e.g., batch vs. streaming event paths), that's stated explicitly in the docs rather than glossed over.

---

## Screenshots

> **📸 Note:** Replace the placeholders below with your own screenshots after
> running `scripts/demo.sh` (or the Windows setup steps). Save images to
> `docs/screenshots/` using the filenames referenced here, then delete this note.
> See [`docs/screenshots.md`](docs/screenshots.md) for the exact list and tips
> on capturing each one well (populate real data first, use a clean browser
> window, avoid capturing personal info in the URL bar).

<table>
<tr>
<td width="50%">

**Dashboard — real, live metrics**
![Dashboard](docs/screenshots/dashboard.png)

</td>
<td width="50%">

**Pipeline run history**
![Pipeline detail](docs/screenshots/pipeline-detail.png)

</td>
</tr>
<tr>
<td width="50%">

**Airflow — orchestrated DAG, all green**
![Airflow DAG](docs/screenshots/airflow-dag.png)

</td>
<td width="50%">

**Grafana — pipeline health dashboard**
![Grafana](docs/screenshots/grafana-pipeline-health.png)

</td>
</tr>
<tr>
<td width="50%">

**Marquez — full lineage graph**
![Lineage](docs/screenshots/marquez-lineage.png)

</td>
<td width="50%">

**Swagger — full API surface**
![Swagger](docs/screenshots/swagger-api.png)

</td>
</tr>
</table>

<details>
<summary><strong>▶ Demo GIF (click to expand once added)</strong></summary>
<br>

![Demo](docs/screenshots/demo.gif)

*Record `scripts/demo.sh` running end-to-end, sped up ~4x, ending on the
Grafana dashboard and frontend both showing live data. Tools like
[ScreenToGif](https://www.screentogif.com/) (Windows) or `asciinema` work well.*

</details>

---

## Architecture

```
                 ┌─────────────────────┐
                 │      DataPulse       │
                 │      SaaS Platform   │
                 └──────────┬──────────┘
                            │
                     FastAPI + Next.js
                            │
                 ┌──────────┴──────────┐
                 │                     │
             PostgreSQL              REST APIs
                 │                     │
                 └──────────┬──────────┘
                            │
                          Kafka
                            │
                    Spark Streaming
                            │
                            ▼
                           S3
                            │
                  Bronze → Silver → Gold
                            │
                       dbt + Spark
                            │
                            ▼
                        Snowflake
                            │
              Airflow · Great Expectations
              OpenLineage · Prometheus/Grafana
              Terraform · GitHub Actions
```

Full diagrams, port maps, and local-vs-production comparisons live in
[`docs/architecture.md`](docs/architecture.md). Every major technology
choice — and the alternatives considered — is recorded as an
[Architecture Decision Record](docs/adr/).

---

## Features

- **Multi-tenant isolation, two layers deep** — app-layer repository scoping + Postgres RLS, composed
- **RBAC** with 5 roles (`OWNER`, `ADMIN`, `DATA_ENGINEER`, `ANALYST`, `VIEWER`), JWT + API-key authentication
- **Batch ingestion** — watermarked incremental extraction, idempotent partition-overwrite writes
- **Kafka streaming** — idempotent producers, keyed partitioning for per-customer ordering
- **Spark batch + Structured Streaming** — bronze→silver→gold, effectively-once via watermark dedup + batch-id partitioning
- **Local-first** — MinIO stands in for S3, a Postgres fallback stands in for Snowflake; the whole platform runs with zero cloud accounts
- **dbt dimensional model** — staging → intermediate → marts, incremental models, 40+ tests
- **Data quality** — Great Expectations suite producing a real, computed quality score
- **Lineage** — OpenLineage (Airflow + Spark) queryable through a tenant-scoped API, full graph in Marquez
- **Monitoring** — Prometheus + Grafana, custom counters/gauges wired at the exact points events occur
- **Next.js dashboard** — 100% real data, RBAC-aware UI
- **CI/CD** — GitHub Actions with real Postgres service containers, not mocks
- **Infrastructure as code** — Terraform for AWS (VPC, RDS, S3, ECS Fargate, IAM least-privilege), dev + prod environments
- **Measured performance work** — every optimization has a before/after number, including two honestly-reported cases where an "optimization" didn't help

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI · SQLAlchemy · Alembic · Pydantic |
| Auth | JWT · API keys (Argon2-hashed) · RBAC |
| Streaming | Apache Kafka (KRaft mode) · confluent-kafka |
| Processing | Apache Spark — batch & Structured Streaming |
| Data Lake | Amazon S3 / MinIO · Parquet · medallion architecture |
| Warehouse | Snowflake (with local PostgreSQL fallback) |
| Transformation | dbt |
| Orchestration | Apache Airflow |
| Data Quality | Great Expectations + dbt tests |
| Lineage | OpenLineage + Marquez |
| Monitoring | Prometheus + Grafana |
| Frontend | Next.js 14 · TypeScript · Tailwind CSS |
| Infrastructure | Docker Compose (local) · Terraform → AWS ECS/RDS/S3 (production) |
| CI/CD | GitHub Actions |

---

## Repository Structure

```
datapulse/
├── backend/          FastAPI control-plane API (auth, RBAC, multi-tenancy)
├── frontend/           Next.js dashboard
├── ingestion/            PostgreSQL → S3/MinIO batch ingestion
├── streaming/              Kafka event producers
├── spark/                    Spark batch + Structured Streaming jobs
├── airflow/                    DAGs
├── dbt/                           dbt project (staging/intermediate/marts)
├── data_quality/                    Great Expectations suites
├── lineage/                           OpenLineage emission/read
├── monitoring/                          Prometheus/Grafana config
├── warehouse/                              Snowflake/Postgres warehouse loader
├── terraform/                                 AWS infrastructure as code
├── scripts/                                     Data generator, benchmark, demo script
├── tests/                                         Cross-cutting integration tests
├── docs/                                            Architecture docs, ADRs, interview prep
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── Makefile
├── .env.example
└── LICENSE
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (WSL2 backend on Windows)
- Python 3.11+
- Node.js 20+ (for the frontend)
- Git

---

## Quick Start

```powershell
git clone https://github.com/YOUR_USERNAME/datapulse.git
cd datapulse

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r scripts/requirements-dev.txt -r backend/requirements.txt -r ingestion/requirements.txt

Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"   # -> JWT_SECRET
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"   # -> DATA_ENCRYPTION_KEY, AIRFLOW__CORE__FERNET_KEY
```

> ⚠️ **Use `.io` / `.dev` / `.com` email domains everywhere** — `.test`,
> `.example`, and `.invalid` are reserved TLDs that `pydantic`'s
> email-validator rejects.

### Start the core stack

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build postgres backend minio adminer
docker compose ps
python scripts/smoke_test_db.py
```

### Apply schemas

> PowerShell has no `<` stdin redirect — use `Get-Content | docker exec -i`.

```powershell
Get-Content infrastructure/postgres/schema/watermarks_schema.sql | docker exec -i datapulse-postgres psql -U datapulse -d datapulse_source
docker exec -it datapulse-postgres psql -U datapulse -d postgres -c "CREATE DATABASE datapulse_test;"
docker exec -it datapulse-postgres psql -U datapulse -d postgres -c "CREATE DATABASE datapulse_warehouse;"
Get-Content infrastructure/postgres_warehouse/schema/warehouse_schemas.sql | docker exec -i datapulse-postgres psql -U datapulse -d datapulse_warehouse
```

### Generate data, register a tenant, run ingestion

```powershell
python scripts/generate_data.py --customers 2000 --orders 8000 --events 30000 --seed 42 --reset

$register = Invoke-RestMethod -Uri http://localhost:8000/auth/register -Method Post -ContentType "application/json" `
  -Body (@{ tenant_slug = "acme"; tenant_name = "ACME Corporation"; email = "owner@acme.io"; password = "supersecret123"; full_name = "Alice Owner" } | ConvertTo-Json)

$login = Invoke-RestMethod -Uri http://localhost:8000/auth/login -Method Post -ContentType "application/json" `
  -Body (@{ tenant_slug = "acme"; email = "owner@acme.io"; password = "supersecret123" } | ConvertTo-Json)
$token = $login.access_token

python -m ingestion.cli --tenant acme --api-token $token
```

### Bring up the rest of the platform, phase by phase

```powershell
# Airflow (orchestration)
docker compose up -d --build airflow-postgres airflow-init airflow-webserver airflow-scheduler

# Kafka + Spark batch
docker compose up -d --build kafka kafka-init kafka-ui
docker compose --profile batch run --rm spark python jobs/batch/bronze_to_silver.py --tenant acme --api-token $token
docker compose --profile batch run --rm spark python jobs/batch/silver_to_gold.py --tenant acme --api-token $token

# Streaming
docker compose --profile streaming up -d --build spark-streaming
python -m streaming.cli --tenant acme --rate 10 --duration 60

# Warehouse + dbt (no Snowflake account needed — uses local Postgres fallback)
python -m warehouse.cli --tenant acme
cd dbt/datapulse; dbt deps; dbt run --target local; dbt test --target local; cd ../..

# Data quality + lineage
docker compose up -d --build marquez-db marquez marquez-web
python -m data_quality.cli --tenant acme --api-token $token

# Monitoring
docker compose up -d --build prometheus grafana kafka-exporter

# Frontend
docker compose up -d --build frontend
```

### Or, all at once (Linux / macOS / WSL)

```bash
chmod +x scripts/demo.sh
./scripts/demo.sh
```

---

## URLs

| Service | URL | Credentials |
|---|---|---|
| Frontend | http://localhost:3000 | tenant `acme` / `owner@acme.io` / `supersecret123` |
| API / Swagger | http://localhost:8000/docs | — |
| Airflow | http://localhost:8080 | `admin` / `admin` |
| Kafka UI | http://localhost:8081 | — |
| MinIO Console | http://localhost:9001 | `minioadmin` / `minioadmin` |
| Grafana | http://localhost:3001 | `admin` / `admin` |
| Prometheus | http://localhost:9090 | — |
| Marquez | http://localhost:3002 | — |
| Adminer | http://localhost:8082 | server: `postgres` |

---

## Testing

```powershell
pytest -v                                                       # generator, ingestion, warehouse, lineage, quality
cd backend; pytest -v                                             # API, tenant isolation, RBAC, RLS
cd ..
docker compose --profile batch run --rm spark pytest tests/ -v      # Spark transformations
cd dbt/datapulse; dbt test --target local                             # warehouse tests
```

---

## AWS Deployment

```powershell
cd terraform/environments/dev
Copy-Item terraform.tfvars.example terraform.tfvars   # fill in real ECR image URIs
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

> ⚠️ **Remember to `terraform destroy` when you're done.** NAT Gateways
> and RDS instances bill hourly even fully idle — see
> [`docs/aws.md`](docs/aws.md) for the full cost breakdown and teardown
> checklist.

---

## Documentation

| Doc | Covers |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | System diagram, port map, local vs. production |
| [`docs/kafka.md`](docs/kafka.md) · [`docs/spark.md`](docs/spark.md) · [`docs/streaming.md`](docs/streaming.md) | Streaming design, partitioning, exactly-once semantics |
| [`docs/dbt.md`](docs/dbt.md) · [`docs/data-quality.md`](docs/data-quality.md) · [`docs/lineage.md`](docs/lineage.md) | Warehouse modeling, quality gates, lineage tracking |
| [`docs/monitoring.md`](docs/monitoring.md) · [`docs/frontend.md`](docs/frontend.md) | Observability, frontend architecture tradeoffs |
| [`docs/aws.md`](docs/aws.md) · [`docs/terraform.md`](docs/terraform.md) · [`docs/ci-cd.md`](docs/ci-cd.md) | Cloud deployment, IaC, pipeline design |
| [`docs/security.md`](docs/security.md) · [`docs/performance.md`](docs/performance.md) | Auth, isolation layers, measured optimizations |
| [`docs/adr/`](docs/adr/) | Architecture Decision Records — why each major technology was chosen |
| [`docs/interview-prep.md`](docs/interview-prep.md) | Full interview guide, organized by topic |

---

## Known Gotchas

Fixed in this codebase, worth knowing if you extend it:

1. **Email domains** — use `.io` / `.dev` / `.com`, never `.test` / `.example` / `.invalid` (reserved TLDs rejected by `email-validator`).
2. **PowerShell has no `<` stdin redirect** — use `Get-Content file.sql | docker exec -i container psql ...`.
3. **YAML indentation in `docker-compose.yml`** — every service must align exactly under `services:`; a misaligned key silently merges into the previous service.
4. **`external: true` vs. `driver: bridge`** — only reference a Docker network as `external: true` in a compose file that *doesn't* create it.

---

## Roadmap / Build Phases

| Phase | Deliverable | Status |
|---|---|---|
| 1–4 | Infra, data generator, FastAPI backend, ingestion + data lake | ✅ |
| 5–6 | Airflow orchestration, Spark batch processing | ✅ |
| 7–8 | Kafka streaming, Spark Structured Streaming | ✅ |
| 9–10 | Snowflake warehouse, dbt dimensional modeling | ✅ |
| 11–12 | Data quality (Great Expectations), lineage (OpenLineage) | ✅ |
| 13–14 | Monitoring (Prometheus/Grafana), Next.js frontend | ✅ |
| 15–16 | CI/CD (GitHub Actions), Terraform + AWS | ✅ |
| 17–18 | Security hardening (API keys, RLS, encryption), performance | ✅ |
| 19–20 | End-to-end demo, docs, ADRs, interview prep | ✅ |

## Future Improvements

- Unify batch and streaming event paths into one `fact_events` model
- Scope API keys to specific permissions rather than inheriting OWNER access
- Full MSK / EMR / MWAA Terraform modules for a 100%-managed production deployment
- Column-level lineage via OpenLineage facets
- Direct Kafka throughput and S3 small-file-vs-compacted read benchmarks

## Lessons Learned

Building this end-to-end surfaced the same lesson repeatedly: the
interesting engineering decisions are rarely *"which technology"* and
almost always *"how do two pieces compose, and what does each one **not**
cover."* Two isolation layers that catch different bugs. Two lineage-
capture mechanisms with different blind spots. Two dedup mechanisms
(producer idempotence, consumer-side event ID dedup) that only *together*
give effectively-once semantics. Naming these compositions precisely —
not just "I used X" — is what turns a project into something defensible
in depth.

---

## License

MIT — see [`LICENSE`](LICENSE).

---

<div align="center">

*If this project was useful as a reference, a ⭐ is appreciated.*

</div>
