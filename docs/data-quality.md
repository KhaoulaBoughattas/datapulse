# DataPulse — Data Quality

## GE (silver) vs. dbt tests (warehouse) — not redundant
| | Great Expectations | dbt tests |
|---|---|---|
| Runs against | Silver Parquet | Warehouse tables |
| Catches | Bad SOURCE data, before warehouse compute cost | Bugs IN the transformation logic |

## Referential integrity without a JOIN
GE has no cross-table JOIN expectation. Precompute the parent table's
primary keys as a Python set; check child-column membership against it.
