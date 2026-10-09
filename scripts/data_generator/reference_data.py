from __future__ import annotations

DEFAULT_TENANTS: list[str] = ["acme", "globex", "initech"]

TENANT_DISPLAY_NAMES: dict[str, str] = {
    "acme": "ACME Corporation",
    "globex": "Globex Corporation",
    "initech": "Initech",
}

PRODUCT_CATEGORIES: dict[str, tuple[float, float]] = {
    "Electronics": (15.0, 1200.0),
    "Home & Kitchen": (8.0, 300.0),
    "Clothing": (5.0, 150.0),
    "Sports & Outdoors": (10.0, 400.0),
    "Books": (5.0, 60.0),
    "Beauty": (4.0, 120.0),
    "Toys & Games": (6.0, 200.0),
}

ORDER_STATUSES: list[str] = ["completed", "pending", "cancelled", "refunded"]
ORDER_STATUS_WEIGHTS: list[float] = [0.70, 0.10, 0.10, 0.10]

PAYMENT_METHODS: list[str] = ["credit_card", "paypal", "bank_transfer", "apple_pay"]

SUBSCRIPTION_PLANS: dict[str, float] = {"basic": 9.99, "pro": 29.99, "enterprise": 99.99}
SUBSCRIPTION_STATUS_WEIGHTS: dict[str, float] = {"active": 0.80, "cancelled": 0.20}

EVENT_TYPES: list[str] = [
    "product_view", "add_to_cart", "checkout", "purchase",
    "login", "subscription_created", "subscription_cancelled",
]
EVENT_TYPE_WEIGHTS: list[float] = [0.45, 0.20, 0.10, 0.10, 0.10, 0.03, 0.02]
PRODUCT_LINKED_EVENT_TYPES: set[str] = {"product_view", "add_to_cart", "purchase"}
DEVICE_TYPES: list[str] = ["desktop", "mobile", "tablet"]

COUNTRIES: list[str] = [
    "United States", "United Kingdom", "Germany", "France", "Canada",
    "Australia", "India", "Brazil", "Spain", "Netherlands",
]
COUNTRY_WEIGHTS: list[float] = [0.35, 0.12, 0.10, 0.08, 0.08, 0.06, 0.08, 0.06, 0.04, 0.03]
