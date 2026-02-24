from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, Optional, TypeVar, cast

T = TypeVar("T")


def setup_logging(level: str = "INFO") -> None:
    """Configure basic console logging for scripts and local runs."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def log(
    logger: logging.Logger, name: Optional[str] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator: log start/end + duration for a function call."""

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        display = name or fn.__name__

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()
            logger.debug("→ %s", display)
            try:
                result = fn(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.debug("← %s (%.2fs)", display, elapsed)
                return result
            except Exception:
                elapsed = time.perf_counter() - start
                logger.exception("✗ %s failed (%.2fs)", display, elapsed)
                raise

        return cast(Callable[..., T], wrapper)

    return decorator
