"""Retry-vs-fail-fast distinction: schema/data errors fail immediately
(no point retrying identical bad input); transient errors (network,
connection) propagate normally and ARE retried per the task's `retries`."""
from __future__ import annotations

import functools
import logging
from collections.abc import Callable

from airflow.exceptions import AirflowFailException
from sqlalchemy.exc import DataError, IntegrityError, ProgrammingError

logger = logging.getLogger("airflow.task")

NON_RETRYABLE_EXCEPTIONS = (ProgrammingError, DataError, IntegrityError, ValueError, KeyError)


def fail_fast_on_data_errors(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NON_RETRYABLE_EXCEPTIONS as exc:
            logger.error("Non-retryable data/schema error in %s: %s", func.__name__, exc)
            raise AirflowFailException(f"Data/schema error (not retrying): {exc}") from exc

    return wrapper
