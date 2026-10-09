#!/usr/bin/env python
"""
DataPulse benchmark harness. Generates data at increasing volumes and
times the host-runnable pipeline stages (generation, ingestion), writing
REAL measured results to benchmarks/results.md.

Usage:
    python scripts/benchmark.py --sizes 10000,100000
"""
from __future__ import annotations
import argparse
import logging
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("benchmark")
RESULTS_PATH = Path(__file__).resolve().parents[1] / "benchmarks" / "results.md"


def _time_command(cmd: list[str]) -> float:
    start = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    if result.returncode != 0:
        logger.error("Command failed: %s\n%s", " ".join(cmd), result.stderr[-2000:])
    return elapsed


def run_benchmark(order_count: int) -> dict[str, float]:
    customer_count = max(200, order_count // 10)
    logger.info("=== Benchmarking at %d orders (%d customers) ===", order_count, customer_count)
    timings = {}
    timings["generate_data"] = _time_command([
        "python", "scripts/generate_data.py", "--customers", str(customer_count), "--products", "100",
        "--orders", str(order_count), "--events", str(order_count * 3), "--seed", "42", "--reset",
    ])
    timings["ingestion"] = _time_command(["python", "-m", "ingestion.cli", "--tenant", "acme"])
    return timings


def write_results(all_results: dict[int, dict[str, float]]) -> None:
    lines = [
        "# DataPulse Benchmark Results", "",
        f"_Generated {datetime.now(timezone.utc).isoformat()}. Real measured timings — "
        "absolute numbers vary by hardware; relative comparisons are the meaningful signal._", "",
        "| Order count | " + " | ".join(next(iter(all_results.values())).keys()) + " |",
        "|---|" + "---|" * len(next(iter(all_results.values()))),
    ]
    for order_count, timings in all_results.items():
        row = " | ".join(f"{t:.2f}s" for t in timings.values())
        lines.append(f"| {order_count:,} | {row} |")
    RESULTS_PATH.parent.mkdir(exist_ok=True)
    RESULTS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Wrote results to %s", RESULTS_PATH)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", type=str, default="10000,100000")
    args = parser.parse_args()
    sizes = [int(s) for s in args.sizes.split(",")]
    all_results = {size: run_benchmark(size) for size in sizes}
    write_results(all_results)


if __name__ == "__main__":
    main()
