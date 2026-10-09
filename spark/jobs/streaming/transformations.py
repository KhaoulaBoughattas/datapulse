"""Pure transformation logic, unit-testable without Kafka."""
from __future__ import annotations
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from spark.jobs.streaming.common.schema import EVENT_SCHEMA


def parse_kafka_events(raw_kafka_df: DataFrame) -> DataFrame:
    return (
        raw_kafka_df.select(F.col("key").cast("string").alias("kafka_key"), F.from_json(F.col("value").cast("string"), EVENT_SCHEMA).alias("event"))
        .select("kafka_key", "event.*")
        .withColumn("event_timestamp", F.to_timestamp("event_timestamp"))
        .withColumn("event_date", F.to_date("event_timestamp"))
    )


def deduplicate_events(parsed_df: DataFrame, watermark_duration: str = "10 minutes") -> DataFrame:
    return parsed_df.withWatermark("event_timestamp", watermark_duration).dropDuplicatesWithinWatermark(["event_id"])


def add_batch_partition_column(df: DataFrame, epoch_id: int) -> DataFrame:
    return df.withColumn("batch_id", F.lit(epoch_id))
