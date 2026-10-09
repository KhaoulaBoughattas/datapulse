# DataPulse — Spark Structured Streaming

## "Effectively-once", precisely
At-least-once delivery (checkpointed offsets) + idempotent processing
(`dropDuplicatesWithinWatermark` by event_id) + idempotent sink
(batch-id-keyed partition overwrite) = effectively-once. Composition of
standard mechanisms, not a single "exactly-once" toggle.

## Two idempotency mechanisms, side by side
- `bronze_stream.py`: `foreachBatch` + batch_id partition — needed for
  custom partition/overwrite control.
- `realtime_aggregates.py`: native file sink, append mode — correct
  because this job only ever appends completed windows.
