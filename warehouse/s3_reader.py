from __future__ import annotations
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.fs as pafs
from warehouse.config import S3ReadConfig


def _filesystem(config: S3ReadConfig) -> pafs.S3FileSystem:
    endpoint = config.endpoint_url.replace("http://", "").replace("https://", "")
    return pafs.S3FileSystem(endpoint_override=endpoint, access_key=config.access_key, secret_key=config.secret_key, scheme="http")


def read_silver_table(config: S3ReadConfig, table_name: str, tenant_id: str | None = None) -> pd.DataFrame:
    base_path = f"{config.bucket}/silver/{table_name}"
    path = f"{base_path}/tenant_id={tenant_id}" if tenant_id else base_path
    dataset = ds.dataset(path, filesystem=_filesystem(config), partitioning="hive", format="parquet")
    df = dataset.to_table().to_pandas()
    if tenant_id and "tenant_id" not in df.columns:
        df["tenant_id"] = tenant_id
    return df
