# ADR 001: Use Apache Kafka for Streaming

## Context
Need a durable, replayable, ordered event transport between producers
(clickstream simulator) and consumers (Spark Structured Streaming).

## Decision
Apache Kafka in KRaft mode (no ZooKeeper).

## Alternatives Considered
- AWS Kinesis: simpler to manage, but ties local dev to AWS from day one.
- Redis Streams: lighter, but lacks Kafka's consumer-group/replay semantics.
- RabbitMQ: queue semantics don't fit "multiple independent consumers replay the same topic."

## Consequences
Requires learning Kafka's partition/consumer-group model — the point,
since it's the most commonly asked-about streaming tech in DE interviews.
