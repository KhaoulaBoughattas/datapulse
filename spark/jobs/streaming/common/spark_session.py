"""SparkSession builder for streaming jobs (adds the Kafka connector on
top of the S3A packages)."""
from __future__ import annotations
import os
from pyspark.sql import SparkSession

_PACKAGES = ",".join([
    "org.apache.hadoop:hadoop-aws:3.3.4",
    "com.amazonaws:aws-java-sdk-bundle:1.12.262",
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3",
    "org.apache.spark:spark-token-provider-kafka-0-10_2.12:3.5.3",
    "org.apache.kafka:kafka-clients:3.8.0",
    "org.apache.commons:commons-pool2:2.11.1",
])


def get_streaming_spark_session(app_name: str) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .master(os.getenv("SPARK_MASTER", "local[*]"))
        .config("spark.jars.packages", _PACKAGES)
        .config("spark.hadoop.fs.s3a.endpoint", os.environ["S3_ENDPOINT_URL"])
        .config("spark.hadoop.fs.s3a.access.key", os.environ["S3_ACCESS_KEY"])
        .config("spark.hadoop.fs.s3a.secret.key", os.environ["S3_SECRET_KEY"])
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )


def bucket_path(bucket: str, *parts: str) -> str:
    return f"s3a://{bucket}/{'/'.join(parts)}"
