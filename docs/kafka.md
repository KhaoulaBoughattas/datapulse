# DataPulse — Kafka Streaming

## Why KRaft, not ZooKeeper
KRaft folds Kafka's metadata management into Kafka itself — the default
since Kafka 3.5, mandatory from Kafka 4.0. No separate coordination
service to run locally.

## Partitioning key strategy
Events keyed by `customer_id` (fallback: `session_id`) — preserves
per-customer ordering across a session. Tradeoff: a very active customer
creates a hot partition, capping their own throughput.

## Producer idempotence — what it does and doesn't guarantee
`enable.idempotence=true` + `acks=all` prevents BROKER-side duplicate
writes from PRODUCER retries within one session. Does NOT protect
against producer crash/restart or consumer-side duplicate processing —
that's why every event carries a unique `event_id` for downstream dedup.
