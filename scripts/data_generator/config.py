from __future__ import annotations

import argparse
from dataclasses import dataclass

from data_generator.reference_data import DEFAULT_TENANTS


@dataclass(frozen=True)
class GeneratorConfig:
    tenants: list[str]
    customers: int
    products: int
    orders: int
    events: int
    subscription_rate: float
    order_items_max: int
    batch_size: int
    seed: int | None
    reset: bool

    def customers_per_tenant(self) -> list[int]:
        return _distribute(self.customers, len(self.tenants))

    def products_per_tenant(self) -> list[int]:
        return _distribute(self.products, len(self.tenants))

    def orders_per_tenant(self) -> list[int]:
        return _distribute(self.orders, len(self.tenants))

    def events_per_tenant(self) -> list[int]:
        return _distribute(self.events, len(self.tenants))


def _distribute(total: int, n: int) -> list[int]:
    if n <= 0:
        raise ValueError("n must be a positive integer")
    base, remainder = divmod(total, n)
    return [base + 1 if i < remainder else base for i in range(n)]


def parse_args(argv: list[str] | None = None) -> GeneratorConfig:
    parser = argparse.ArgumentParser(prog="generate_data.py")
    parser.add_argument("--tenants", type=str, default=",".join(DEFAULT_TENANTS))
    parser.add_argument("--customers", type=int, default=2000)
    parser.add_argument("--products", type=int, default=300)
    parser.add_argument("--orders", type=int, default=8000)
    parser.add_argument("--events", type=int, default=30000)
    parser.add_argument("--subscription-rate", type=float, default=0.20)
    parser.add_argument("--order-items-max", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--reset", action="store_true")

    args = parser.parse_args(argv)
    tenants = [t.strip() for t in args.tenants.split(",") if t.strip()]
    if not tenants:
        parser.error("--tenants must contain at least one non-empty slug")

    return GeneratorConfig(
        tenants=tenants,
        customers=args.customers,
        products=args.products,
        orders=args.orders,
        events=args.events,
        subscription_rate=args.subscription_rate,
        order_items_max=max(1, args.order_items_max),
        batch_size=max(1, args.batch_size),
        seed=args.seed,
        reset=args.reset,
    )
