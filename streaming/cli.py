#!/usr/bin/env python
"""DataPulse streaming event producer CLI.

Usage:
    python -m streaming.cli --tenant acme --count 500
    python -m streaming.cli --tenant acme --rate 20 --duration 60
"""
from __future__ import annotations
import argparse
import logging
import random
import time
from dotenv import load_dotenv
from streaming.config import load_config
from streaming.producer import build_producer, send_event
from streaming.simulator import EventSimulator
from streaming.source_lookup import load_customer_and_product_ids, load_tenant_ids

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("streaming.cli")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="DataPulse Kafka event producer")
    parser.add_argument("--tenant", type=str)
    parser.add_argument("--all-tenants", action="store_true")
    parser.add_argument("--count", type=int, default=None)
    parser.add_argument("--rate", type=float, default=None)
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if not args.tenant and not args.all_tenants:
        parser.error("Provide --tenant <slug> or --all-tenants")
    if args.count is None and (args.rate is None or args.duration is None):
        parser.error("Provide --count, or both --rate and --duration")

    config = load_config()
    tenant_ids = load_tenant_ids(config) if args.all_tenants else [args.tenant]
    producer = build_producer(config)

    grand_totals: dict[str, int] = {}
    for idx, tenant_id in enumerate(tenant_ids):
        rng = random.Random(None if args.seed is None else args.seed + idx)
        customer_ids, product_ids = load_customer_and_product_ids(config, tenant_id)
        simulator = EventSimulator(tenant_id, customer_ids, product_ids, rng)

        if args.count is not None:
            totals = simulator.run(producer, args.count)
        else:
            end_time = time.time() + args.duration
            interval = 1.0 / args.rate
            totals: dict[str, int] = {}
            while time.time() < end_time:
                for topic, event in simulator.generate_next():
                    send_event(producer, topic, event)
                    totals[topic] = totals.get(topic, 0) + 1
                time.sleep(interval)
            producer.flush(timeout=10)

        for topic, count in totals.items():
            grand_totals[topic] = grand_totals.get(topic, 0) + count
        logger.info("[%s] Done: %s", tenant_id, totals)

    logger.info("PRODUCTION COMPLETE: %s", grand_totals)


if __name__ == "__main__":
    main()
