#!/usr/bin/env python
"""Real-time windowed event-count aggregation using Structured
Streaming's native file sink (append mode) — appropriate since this job
only ever appends new completed windows."""
from __future__ import annotations
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.streaming import StreamingQuery
from spark.jobs.streaming.common.spark_session import bucket_path
from spark.jobs.streaming.transformations import parse_kafka_events

TOPICS = "user-events,order-events,payment-events"


def start_realtime_aggregates(spark: SparkSession) -> StreamingQuery:
    bucket = os.environ["S3_BUCKET"]
    checkpoint_path = os.environ["STREAMING_CHECKPOINT_DIR"] + "/realtime_aggregates"
    output_path = bucket_path(bucket, "gold_streaming", "events_per_minute")

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", os.environ["KAFKA_BOOTSTRAP_SERVERS"])
        .option("subscribe", TOPICS)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .load()
    )
    parsed = parse_kafka_events(raw)

    windowed_counts = (
        parsed.withWatermark("event_timestamp", "10 minutes")
        .groupBy(F.window("event_timestamp", "1 minute"), F.col("tenant_id"), F.col("event_type"))
        .count()
        .select(F.col("tenant_id"), F.col("event_type"), F.col("window.start").alias("window_start"),
                 F.col("window.end").alias("window_end"), F.col("count").alias("event_count"))
    )

    return (
        windowed_counts.writeStream.outputMode("append").format("parquet")
        .option("path", output_path).option("checkpointLocation", checkpoint_path)
        .partitionBy("tenant_id").trigger(processingTime="30 seconds").start()
    )
