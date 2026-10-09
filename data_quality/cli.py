#!/usr/bin/env python
"""DataPulse data quality CLI.

Usage:
    python -m data_quality.cli --tenant acme --api-token <token>
"""
from __future__ import annotations
import argparse
import logging
from dotenv import load_dotenv
from data_quality.runner import run_quality_checks
from ingestion.api_client import DataPulseApiClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("data_quality.cli")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run DataPulse data quality checks against silver data")
    parser.add_argument("--tenant", type=str, required=True)
    parser.add_argument("--api-token", type=str, default=None)
    parser.add_argument("--api-base-url", type=str, default="http://localhost:8000")
    parser.add_argument("--fail-below", type=float, default=None)
    args = parser.parse_args()

    api_client = DataPulseApiClient(args.api_base_url, args.api_token) if args.api_token else None
    try:
        results, overall_score = run_quality_checks(args.tenant, api_client)
    finally:
        if api_client is not None:
            api_client.close()

    failed = [r for r in results if not r.passed]
    logger.info("DATA QUALITY SCORE: %.2f%%  (%d checks, %d failed)", overall_score, len(results), len(failed))
    for r in failed:
        logger.warning("  FAILED: %s (score=%.2f)", r.check_name, r.score)

    if args.fail_below is not None and overall_score < args.fail_below:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
