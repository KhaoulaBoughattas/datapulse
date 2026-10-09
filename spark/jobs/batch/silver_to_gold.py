#!/usr/bin/env python
"""DataPulse — Silver to Gold batch job. Builds gold/revenue,
gold/customer_360, gold/product_analytics via joins/aggregations."""
from __future__ import annotations
import argparse
import logging
import os
import sys

from dotenv import load_dotenv
from pyspark.sql import functions as F

sys.path.insert(0, "/opt/app")

from ingestion.api_client import DataPulseApiClient  # noqa: E402
from jobs.batch.common.spark_session import bucket_path, get_spark_session  # noqa: E402
from jobs.batch.common.tenants import list_tenant_ids  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("silver_to_gold")


def build_revenue(spark, bucket: str, tenant_id: str):
    orders = spark.read.parquet(bucket_path(bucket, "silver", "orders")).filter(F.col("tenant_id") == tenant_id)
    payments = spark.read.parquet(bucket_path(bucket, "silver", "payments")).filter(F.col("tenant_id") == tenant_id)
    successful_payments = payments.filter(F.col("status") == "success")

    return (
        orders.join(successful_payments, on="order_id", how="inner")
        .withColumn("order_month", F.date_format("order_date", "yyyy-MM"))
        .groupBy("tenant_id", "order_month")
        .agg(F.sum("amount").alias("total_revenue"), F.count("order_id").alias("order_count"))
        .withColumn("average_order_value", F.round(F.col("total_revenue") / F.col("order_count"), 2))
        .coalesce(1)
    )


def build_customer_360(spark, bucket: str, tenant_id: str):
    customers = spark.read.parquet(bucket_path(bucket, "silver", "customers")).filter(F.col("tenant_id") == tenant_id)
    orders = spark.read.parquet(bucket_path(bucket, "silver", "orders")).filter(F.col("tenant_id") == tenant_id)
    subscriptions = spark.read.parquet(bucket_path(bucket, "silver", "subscriptions")).filter(F.col("tenant_id") == tenant_id)

    order_agg = orders.groupBy("customer_id").agg(
        F.count("order_id").alias("lifetime_orders"), F.sum("total_amount").alias("lifetime_revenue"),
        F.min("order_date").alias("first_order_date"), F.max("order_date").alias("last_order_date"),
    )
    active_subs = (
        subscriptions.filter(F.col("status") == "active").select("customer_id")
        .withColumn("has_active_subscription", F.lit(True)).dropDuplicates(["customer_id"])
    )

    return (
        F.broadcast(customers).join(order_agg, on="customer_id", how="left")
        .join(F.broadcast(active_subs), on="customer_id", how="left")
        .fillna({"lifetime_orders": 0, "lifetime_revenue": 0.0, "has_active_subscription": False})
        .select("customer_id", "tenant_id", "first_name", "last_name", "email", "country",
                "lifetime_orders", "lifetime_revenue", "first_order_date", "last_order_date", "has_active_subscription")
        .coalesce(4)
    )


def build_product_analytics(spark, bucket: str, tenant_id: str):
    products = spark.read.parquet(bucket_path(bucket, "silver", "products")).filter(F.col("tenant_id") == tenant_id)
    order_items = spark.read.parquet(bucket_path(bucket, "silver", "order_items")).filter(F.col("tenant_id") == tenant_id)
    events = spark.read.parquet(bucket_path(bucket, "silver", "events")).filter(
        (F.col("tenant_id") == tenant_id) & (F.col("event_type") == "product_view")
    )

    sales_agg = order_items.groupBy("product_id").agg(
        F.sum("quantity").alias("units_sold"), F.sum(F.col("quantity") * F.col("unit_price")).alias("revenue")
    )
    view_agg = events.groupBy("product_id").agg(F.count("event_id").alias("view_count"))

    return (
        F.broadcast(products).join(sales_agg, on="product_id", how="left").join(view_agg, on="product_id", how="left")
        .fillna({"units_sold": 0, "revenue": 0.0, "view_count": 0})
        .select("product_id", "tenant_id", "name", "category", "units_sold", "revenue", "view_count")
        .coalesce(2)
    )


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Silver -> Gold batch processing")
    parser.add_argument("--tenant", type=str)
    parser.add_argument("--all-tenants", action="store_true")
    parser.add_argument("--api-token", type=str, default=None)
    parser.add_argument("--api-base-url", type=str, default=os.getenv("DATAPULSE_API_BASE_URL", "http://backend:8000"))
    args = parser.parse_args()

    if not args.tenant and not args.all_tenants:
        parser.error("Provide --tenant <slug> or --all-tenants")

    bucket = os.environ["S3_BUCKET"]
    tenant_ids = list_tenant_ids() if args.all_tenants else [args.tenant]

    api_client = DataPulseApiClient(args.api_base_url, args.api_token) if args.api_token else None
    pipeline_id, run_id, total_rows = None, None, 0

    spark = get_spark_session("silver_to_gold")
    try:
        if api_client:
            pipeline_id = api_client.get_or_create_pipeline("silver_to_gold_batch", "BATCH")
            run_id = api_client.start_pipeline_run(pipeline_id)

        for tenant_id in tenant_ids:
            gold_specs = [
                ("revenue", build_revenue(spark, bucket, tenant_id), ["tenant_id"]),
                ("customer_360", build_customer_360(spark, bucket, tenant_id), ["tenant_id"]),
                ("product_analytics", build_product_analytics(spark, bucket, tenant_id), ["tenant_id"]),
            ]
            for name, df, partition_cols in gold_specs:
                row_count = df.count()
                path = bucket_path(bucket, "gold", name)
                df.write.mode("overwrite").partitionBy(*partition_cols).parquet(path)
                total_rows += row_count
                logger.info("[%s] Wrote %d rows to gold/%s", tenant_id, row_count, name)
                if api_client and pipeline_id and row_count > 0:
                    api_client.register_dataset(name=f"gold_{name}", layer="GOLD", location=f"{path}/tenant_id={tenant_id}/", pipeline_id=pipeline_id)

        if api_client and run_id:
            api_client.finish_pipeline_run(run_id, status="SUCCESS", records_processed=total_rows)
        logger.info("SILVER -> GOLD COMPLETE — %d total rows written", total_rows)

    except Exception as exc:
        if api_client and run_id:
            api_client.finish_pipeline_run(run_id, status="FAILED", records_processed=total_rows, error_message=str(exc))
        raise
    finally:
        spark.stop()
        if api_client:
            api_client.close()


if __name__ == "__main__":
    main()
