"""
Logging utilities for Rajniti.

* ``GracefulFormatter`` — colour-coded, **condensed tracebacks** (last N
  frames only) so that parallel agent failures don't flood the terminal.
* ``setup_logging``     — one-liner to wire the formatter for CLI scripts.
* ``log``               — timing / error-reporting decorator used on every
  agent method.
"""

from __future__ import annotations

import functools
import logging
import sys
import time
import traceback
from typing import Any, Callable, Optional, TypeVar, cast

T = TypeVar("T")

# ---------------------------------------------------------------------------
# ANSI helpers
# ---------------------------------------------------------------------------


class _C:
    """Namespace for ANSI escape codes."""

    RESET = "\033[0m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    MAGENTA = "\033[95m"


def _has_color() -> bool:
    return hasattr(sys.stderr, "isatty") and sys.stderr.isatty()


_USE_COLOR: bool = _has_color()


def _paint(code: str, text: str) -> str:
    if not _USE_COLOR:
        return text
    return f"{code}{text}{_C.RESET}"


# ---------------------------------------------------------------------------
# GracefulFormatter
# ---------------------------------------------------------------------------


class GracefulFormatter(logging.Formatter):
    """Compact, colour-coded formatter that **condenses tracebacks**.

    * DEBUG     → dim
    * INFO      → green
    * WARNING   → yellow
    * ERROR+    → red / bold-red
    * Tracebacks are trimmed to the last ``MAX_TB_FRAMES`` frames.
    """

    MAX_TB_FRAMES: int = 3
    MAX_MSG_LEN: int = 500

    _LEVEL_COLOR = {
        logging.DEBUG: _C.DIM,
        logging.INFO: _C.GREEN,
        logging.WARNING: _C.YELLOW,
        logging.ERROR: _C.RED,
        logging.CRITICAL: f"{_C.BOLD}{_C.RED}",
    }

    def format(self, record: logging.LogRecord) -> str:
        ts = self.formatTime(record, "%H:%M:%S")

        color = self._LEVEL_COLOR.get(record.levelno, "")
        level = _paint(color, f"{record.levelname:<8}")

        name = self._abbreviate(record.name)
        name = _paint(_C.CYAN, name)

        msg = record.getMessage()
        if len(msg) > self.MAX_MSG_LEN:
            msg = msg[: self.MAX_MSG_LEN] + "…"

        line = f"{_paint(_C.DIM, ts)} | {level} | {name} | {msg}"

        if record.exc_info and record.exc_info[1] is not None:
            line += "\n" + self._condensed_tb(record.exc_info)
            record.exc_info = None
            record.exc_text = None

        return line

    # -- helpers ---------------------------------------------------------------

    @staticmethod
    def _abbreviate(name: str, max_len: int = 32) -> str:
        if len(name) <= max_len:
            return name
        parts = name.split(".")
        return ".".join(p[0] if i < len(parts) - 1 else p for i, p in enumerate(parts))

    def _condensed_tb(self, exc_info: tuple[Any, ...]) -> str:
        _, exc_val, exc_tb = exc_info
        if exc_tb is None:
            return _paint(_C.RED, f"  {type(exc_val).__name__}: {exc_val}")

        frames = traceback.extract_tb(exc_tb)
        tail = frames[-self.MAX_TB_FRAMES :]

        lines: list[str] = []
        hidden = len(frames) - len(tail)
        if hidden > 0:
            lines.append(_paint(_C.DIM, f"  ··· {hidden} frame(s) hidden ···"))

        for f in tail:
            short_file = f.filename.rsplit("/", 1)[-1]
            loc = f"{short_file}:{f.lineno} in {f.name}"
            lines.append(_paint(_C.DIM, f"  {loc}"))
            if f.line:
                lines.append(_paint(_C.DIM, f"    {f.line.strip()}"))

        exc_type_name = _paint(_C.RED, type(exc_val).__name__)
        exc_msg = str(exc_val)
        if len(exc_msg) > self.MAX_MSG_LEN:
            exc_msg = exc_msg[: self.MAX_MSG_LEN] + "…"
        lines.append(f"  {exc_type_name}: {exc_msg}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# setup_logging
# ---------------------------------------------------------------------------


def setup_logging(level: str = "INFO") -> None:
    """Configure console logging with the graceful formatter.

    Safe to call multiple times — existing handlers are replaced.
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(GracefulFormatter())
    root.addHandler(handler)


# ---------------------------------------------------------------------------
# @log decorator
# ---------------------------------------------------------------------------


def log(
    logger: logging.Logger, name: Optional[str] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator: log start / end + duration for a function call.

    On exception the traceback rendering is delegated to the
    ``GracefulFormatter`` — no change needed here.
    """

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
