#!/usr/bin/env python
"""Orchestrates a full data quality run for one tenant."""
from __future__ import annotations
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ingestion.api_client import DataPulseApiClient  # noqa: E402
from warehouse.config import load_s3_config  # noqa: E402
from warehouse.s3_reader import read_silver_table  # noqa: E402
from data_quality.checks import add_expectations, build_validator, get_ephemeral_context  # noqa: E402
from data_quality.config import TABLE_CONFIGS  # noqa: E402
from data_quality.scoring import CheckResult, aggregate_score, extract_check_results  # noqa: E402

logger = logging.getLogger("data_quality.runner")


def run_quality_checks(tenant_id: str, api_client: DataPulseApiClient | None = None) -> tuple[list[CheckResult], float]:
    s3_config = load_s3_config()

    dataframes = {}
    for cfg in TABLE_CONFIGS:
        df = read_silver_table(s3_config, cfg.table_name, tenant_id)
        dataframes[cfg.table_name] = df
        logger.info("[%s] Loaded %d rows for '%s'", tenant_id, len(df), cfg.table_name)

    parent_id_sets: dict[str, set] = {}
    for cfg in TABLE_CONFIGS:
        if cfg.unique_columns:
            pk_column = cfg.unique_columns[0]
            df = dataframes[cfg.table_name]
            if pk_column in df.columns:
                parent_id_sets[cfg.table_name] = set(df[pk_column].dropna().tolist())

    context = get_ephemeral_context()
    all_results: list[CheckResult] = []

    for cfg in TABLE_CONFIGS:
        df = dataframes[cfg.table_name]
        if df.empty:
            logger.warning("[%s] No silver data for '%s' — skipping checks.", tenant_id, cfg.table_name)
            continue

        validator = build_validator(context, cfg.table_name, df)
        add_expectations(validator, cfg, parent_id_sets)
        validation_result = validator.validate()

        table_results = extract_check_results(cfg.table_name, validation_result)
        all_results.extend(table_results)

        for check in table_results:
            status = "PASS" if check.passed else "FAIL"
            logger.info("  [%s] %-55s score=%6.2f  %s", tenant_id, check.check_name, check.score, status)
            if api_client is not None:
                api_client.register_quality_result(check_name=check.check_name, passed=check.passed, score=check.score, details=check.details)

    overall_score = aggregate_score(all_results)
    return all_results, overall_score
