# DataPulse — Architecture

## System diagram

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

## Port map

| Service | Port |
|---|---|
| PostgreSQL | 5432 |
| Adminer | 8082 |
| FastAPI (+ /docs) | 8000 |
| MinIO API / Console | 9000 / 9001 |
| Airflow | 8080 |
| Kafka (external) / Kafka UI | 9094 / 8081 |
| Spark UI (batch/streaming) | 4040 / 4041 |
| Marquez API / Web | 5000 / 3002 |
| Prometheus | 9090 |
| Grafana | 3001 |
| Next.js frontend | 3000 |

## Multi-tenancy model

Every tenant-scoped table carries `tenant_id`. Isolation is enforced at
TWO independent layers: application-layer (`TenantScopedRepository`,
Phase 3) and database-layer (Postgres Row-Level Security, Phase 17).
See `docs/security.md` for the precise failure-mode distinction between them.

## Local vs. Production

| Component | Local | Production |
|---|---|---|
| Control-plane DB | Docker Postgres | AWS RDS |
| Object storage | MinIO | AWS S3 |
| Streaming | Docker Kafka (KRaft) | Amazon MSK |
| Compute | Local Spark (Docker) | EMR / Spark-on-EKS |
| Warehouse | Snowflake trial or local Postgres fallback | Snowflake |
| Secrets | `.env` | AWS Secrets Manager |

## Known gotchas (already fixed in this codebase)

1. **Email domains**: `.io`/`.dev`/`.com`, never `.test`/`.example`/`.invalid`.
2. **PowerShell has no `<` stdin redirect**: use `Get-Content file.sql | docker exec -i ...`.
3. **YAML indentation**: every service must align exactly under `services:`.
4. **`external: true` vs `driver: bridge`**: only in a file that doesn't create the network.
