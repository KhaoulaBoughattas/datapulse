# DataPulse — CI/CD

## Why real Postgres service containers, not mocks
Every test exercises real SQL/transactions/FK enforcement — mocking the
database would test nothing meaningful.

## Why Terraform CI never runs apply
Auto-applying on every push means a bad PR could provision/destroy real
infrastructure before human review. `plan` only; `apply` stays a
deliberate, human-triggered action.
