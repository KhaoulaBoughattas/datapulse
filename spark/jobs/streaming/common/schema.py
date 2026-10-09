from pyspark.sql.types import DoubleType, IntegerType, LongType, StringType, StructField, StructType

EVENT_SCHEMA = StructType([
    StructField("event_id", StringType(), nullable=False),
    StructField("schema_version", IntegerType(), nullable=True),
    StructField("tenant_id", StringType(), nullable=False),
    StructField("session_id", StringType(), nullable=True),
    StructField("event_type", StringType(), nullable=False),
    StructField("event_timestamp", StringType(), nullable=False),
    StructField("produced_at", StringType(), nullable=True),
    StructField("customer_id", LongType(), nullable=True),
    StructField("product_id", LongType(), nullable=True),
    StructField("amount", DoubleType(), nullable=True),
    StructField("device_type", StringType(), nullable=True),
    StructField("correlates_with_event_id", StringType(), nullable=True),
])
