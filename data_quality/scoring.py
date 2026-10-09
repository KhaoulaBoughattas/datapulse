"""Converts GE validation results into DataPulse CheckResult records."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CheckResult:
    table_name: str
    check_name: str
    passed: bool
    score: float
    details: dict[str, Any]


def extract_check_results(table_name: str, ge_validation_result) -> list[CheckResult]:
    results: list[CheckResult] = []
    for expectation_result in ge_validation_result.results:
        cfg = expectation_result.expectation_config
        column = cfg.kwargs.get("column", "table")
        check_name = f"{table_name}.{column}.{cfg.expectation_type}"
        result_dict = expectation_result.result or {}
        unexpected_percent = result_dict.get("unexpected_percent")

        score = round(100.0 - unexpected_percent, 2) if unexpected_percent is not None else (100.0 if expectation_result.success else 0.0)

        results.append(CheckResult(
            table_name=table_name, check_name=check_name, passed=bool(expectation_result.success), score=score,
            details={
                "expectation_type": cfg.expectation_type,
                "kwargs": {k: v for k, v in cfg.kwargs.items() if k != "value_set"},
                "element_count": result_dict.get("element_count"),
                "unexpected_count": result_dict.get("unexpected_count"),
                "unexpected_percent": unexpected_percent,
            },
        ))
    return results


def aggregate_score(all_results: list[CheckResult]) -> float:
    if not all_results:
        return 0.0
    return round(sum(r.score for r in all_results) / len(all_results), 2)
