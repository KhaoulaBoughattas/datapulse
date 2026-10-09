#!/usr/bin/env python
"""Streaming entrypoint — starts both queries in one Spark session/process."""
from __future__ import annotations
import logging
from dotenv import load_dotenv
from spark.jobs.streaming.bronze_stream import start_bronze_stream
from spark.jobs.streaming.common.spark_session import get_streaming_spark_session
from spark.jobs.streaming.realtime_aggregates import start_realtime_aggregates

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("streaming.main")


def main() -> None:
    load_dotenv()
    spark = get_streaming_spark_session("datapulse-streaming")
    spark.sparkContext.setLogLevel("WARN")

    logger.info("Starting bronze_stream...")
    bronze_query = start_bronze_stream(spark)
    logger.info("Starting realtime_aggregates...")
    aggregates_query = start_realtime_aggregates(spark)

    logger.info("Both streaming queries running. Awaiting termination...")
    spark.streams.awaitAnyTermination()

    for query in (bronze_query, aggregates_query):
        if not query.isActive and query.exception() is not None:
            logger.error("Query terminated with exception: %s", query.exception())


if __name__ == "__main__":
    main()
