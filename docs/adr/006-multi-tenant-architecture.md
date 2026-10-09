# ADR 006: Multi-Tenant Architecture — Application Layer + RLS, Composed

## Context
Multiple tenants' data must never leak across tenant boundaries, at any layer.

## Decision
Two independent, composed isolation layers: TenantScopedRepository
(application layer) PLUS Postgres Row-Level Security (database layer).

## Alternatives Considered
- RLS only: doesn't help application-layer ergonomics for the 99% of
  code going through the ORM.
- Separate databases per tenant: strongest isolation, but operationally
  heavy for this project's scale.

## Consequences
Two layers to maintain — documented with a precise failure-mode table
(docs/security.md) showing what each catches that the other doesn't.
