#!/usr/bin/env python
"""Kafka -> Bronze streaming job. Dedups by event_id within a watermark
window; writes bronze Parquet partitioned by (tenant_id, event_date,
batch_id) — batch_id makes foreachBatch idempotent across restarts."""
from __future__ import annotations
import logging
import os
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.streaming import StreamingQuery
from spark.jobs.streaming.common.spark_session import bucket_path
from spark.jobs.streaming.transformations import add_batch_partition_column, deduplicate_events, parse_kafka_events

logger = logging.getLogger("bronze_stream")
TOPICS = "user-events,order-events,payment-events"


def start_bronze_stream(spark: SparkSession) -> StreamingQuery:
    bucket = os.environ["S3_BUCKET"]
    checkpoint_path = os.environ["STREAMING_CHECKPOINT_DIR"] + "/bronze_stream"
    output_path = bucket_path(bucket, "bronze", "streaming_events")

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", os.environ["KAFKA_BOOTSTRAP_SERVERS"])
        .option("subscribe", TOPICS)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .load()
    )
    parsed = parse_kafka_events(raw)
    deduped = deduplicate_events(parsed)

    def write_batch(batch_df: DataFrame, epoch_id: int) -> None:
        if batch_df.isEmpty():
            logger.info("Batch %d: empty, skipping write.", epoch_id)
            return
        batch_df = add_batch_partition_column(batch_df, epoch_id)
        row_count = batch_df.count()
        batch_df.write.mode("overwrite").partitionBy("tenant_id", "event_date", "batch_id").parquet(output_path)
        logger.info("Batch %d: wrote %d rows to %s", epoch_id, row_count, output_path)

    return (
        deduped.writeStream.foreachBatch(write_batch)
        .option("checkpointLocation", checkpoint_path)
        .trigger(processingTime="15 seconds")
        .start()
    )
