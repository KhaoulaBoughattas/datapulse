from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LineageConfig:
    marquez_url: str
    namespace: str


def load_config() -> LineageConfig:
    return LineageConfig(marquez_url=os.getenv("MARQUEZ_URL", "http://localhost:5000"), namespace=os.getenv("OPENLINEAGE_NAMESPACE", "datapulse"))
