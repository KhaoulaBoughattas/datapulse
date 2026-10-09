# DataPulse — Security (Consolidated)

## Multi-tenancy: two independent isolation layers

| | Application layer | Database layer / RLS |
|---|---|---|
| Mechanism | `TenantScopedRepository` filters every query by `tenant_id` from the JWT | Postgres RLS policies check a session variable (`app.current_tenant_id`), set by `require_permission()` |
| Catches | The normal, everyday code path | Bugs that bypass the ORM entirely — raw SQL, a forgotten filter, ad-hoc admin queries |
| Does NOT catch | Bugs in code that bypasses TenantScopedRepository | A broken/forged JWT upstream |

## Authentication

- Interactive users: JWT (HS256), Argon2 password hashing.
- Automation (Airflow, scripts): API keys (`dp_live_...`), Argon2-hashed,
  prefix-indexed, shown once at creation.
- **Known limitation**: API keys currently authenticate as the tenant's
  OWNER user (full permissions), not a scoped subset. A `scopes` column
  on `ApiKey` is the natural next hardening step.

## Encryption at rest

`data_sources.connection_config` is encrypted at the APPLICATION layer
(Fernet, `DATA_ENCRYPTION_KEY`) on top of RDS/Postgres's own disk-level
encryption — protects against backups/dumps/replicas with looser access
controls, which disk encryption alone doesn't cover.

## Secrets by environment

| Environment | Storage |
|---|---|
| Local dev | `.env` (gitignored) |
| CI | GitHub Secrets |
| Production | AWS Secrets Manager, Terraform-generated random passwords |

Never committed: `.env`, real credentials, JWT secrets, the data
encryption key, real API keys.
