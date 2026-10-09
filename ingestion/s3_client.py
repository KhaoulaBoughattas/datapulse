from __future__ import annotations

import logging
import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError
from ingestion.config import IngestionConfig

logger = logging.getLogger("ingestion.s3_client")


def get_s3_client(config: IngestionConfig):
    return boto3.client(
        "s3",
        endpoint_url=config.s3_endpoint_url,
        aws_access_key_id=config.s3_access_key,
        aws_secret_access_key=config.s3_secret_key,
        region_name=config.s3_region,
        config=BotoConfig(signature_version="s3v4"),
    )


def ensure_bucket_exists(config: IngestionConfig) -> None:
    client = get_s3_client(config)
    try:
        client.head_bucket(Bucket=config.s3_bucket)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in ("404", "NoSuchBucket"):
            client.create_bucket(Bucket=config.s3_bucket)
            logger.info("Created bucket '%s'.", config.s3_bucket)
        else:
            raise
