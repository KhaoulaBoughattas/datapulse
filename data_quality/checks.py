"""Builds and runs a Great Expectations Validator per table."""
from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
import great_expectations as gx
import pandas as pd
from great_expectations.data_context import AbstractDataContext
from data_quality.config import TableQualityConfig

logger = logging.getLogger("data_quality.checks")


def get_ephemeral_context() -> AbstractDataContext:
    return gx.get_context(mode="ephemeral")


def build_validator(context: AbstractDataContext, table_name: str, df: pd.DataFrame):
    datasource = context.sources.add_or_update_pandas(name="datapulse_pandas_datasource")
    asset = datasource.add_dataframe_asset(name=table_name)
    batch_request = asset.build_batch_request(dataframe=df)
    suite_name = f"{table_name}_suite"
    suite = context.add_or_update_expectation_suite(expectation_suite_name=suite_name)
    return context.get_validator(batch_request=batch_request, expectation_suite=suite)


def add_expectations(validator, config: TableQualityConfig, parent_id_sets: dict[str, set]) -> None:
    validator.expect_table_columns_to_match_set(column_set=list(config.expected_columns), exact_match=False)

    for column in config.not_null_columns:
        validator.expect_column_values_to_not_be_null(column)
    for column in config.unique_columns:
        validator.expect_column_values_to_be_unique(column)
    for column in config.non_negative_columns:
        validator.expect_column_values_to_be_between(column, min_value=0, max_value=None)
    for column, values in config.accepted_values.items():
        validator.expect_column_values_to_be_in_set(column, value_set=values)

    for fk in config.foreign_keys:
        valid_ids = parent_id_sets.get(fk.parent_table, set())
        validator.expect_column_values_to_be_in_set(fk.child_column, value_set=list(valid_ids))

    if config.future_timestamp_column:
        cutoff = datetime.now(timezone.utc) + timedelta(minutes=5)
        validator.expect_column_values_to_be_between(config.future_timestamp_column, min_value=None, max_value=cutoff)
