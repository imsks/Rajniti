"""
BaseAgent — shared foundation for every Rajniti agent.

Provides LLM invocation, JSON parsing, and validation helpers.
Source ingestion uses browser-use directly (see app/sources/, app/browser/).
"""

from __future__ import annotations

import json
import logging
import os
import time
import traceback
from typing import Any, Dict, Optional, TypeVar

from pydantic import TypeAdapter, ValidationError

from app.config.agent_config import get_agent_llm
from app.core import log

T = TypeVar("T")

logger = logging.getLogger(__name__)


def _llm_response_logging_enabled() -> bool:
    v = (os.getenv("RAJNITI_LOG_LLM_RESPONSES") or "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _llm_response_log_max_chars() -> int:
    raw = (os.getenv("RAJNITI_LLM_RESPONSE_LOG_MAX_CHARS") or "").strip()
    if not raw:
        return 1_048_576
    try:
        n = int(raw)
        return n
    except ValueError:
        return 1_048_576


class BaseAgent:
    """Base class inherited by all Rajniti agents."""

    def __init__(self) -> None:
        self.llm = get_agent_llm()
        self._errors: list[dict[str, Any]] = []
        self._llm_call_count = 0

    # ── Error collector ──────────────────────────────────────────────────────

    def _record_error(
        self,
        category: str,
        message: str,
        *,
        context: str = "",
        exc: Optional[Exception] = None,
    ) -> None:
        """Append a structured error entry for later summary."""
        entry: dict[str, Any] = {"category": category, "message": message}
        if context:
            entry["context"] = context
        if exc:
            entry["type"] = type(exc).__name__
            tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
            entry["traceback_tail"] = "".join(tb[-3:]).strip()
        self._errors.append(entry)

    def get_error_summary(self) -> list[dict[str, Any]]:
        """Return all recorded errors (read-only copy)."""
        return list(self._errors)

    def clear_errors(self) -> None:
        """Reset the per-run error log."""
        self._errors.clear()

    def print_error_summary(self) -> None:
        """Log a human-readable error summary at WARNING level."""
        if not self._errors:
            return
        by_cat: dict[str, int] = {}
        for e in self._errors:
            cat = e.get("category", "unknown")
            by_cat[cat] = by_cat.get(cat, 0) + 1
        parts = [f"{cat}={n}" for cat, n in sorted(by_cat.items())]
        logger.warning(
            "Error summary (%d total): %s", len(self._errors), ", ".join(parts)
        )
        for i, e in enumerate(self._errors, 1):
            logger.warning(
                "  [%d] [%s] %s%s",
                i,
                e.get("category"),
                e.get("message", "")[:200],
                f" | ctx={e['context'][:80]}" if e.get("context") else "",
            )

    # ── Politician context (primary sources only — no web tools) ─────────────

    def _gather_politician_context(self, politician: Dict[str, Any]) -> str:
        """Known primary source URLs from field-level citations."""
        from app.sources.provenance import PRIMARY_SOURCES, citation_source

        parts: list[str] = []
        ref_lines: list[str] = []

        fd = politician.get("financial_disclosure") or {}
        fd_cite = fd.get("citation") or {}
        if fd_cite.get("link"):
            ref_lines.append(f"affidavit: {fd_cite['link']}")

        for section in ("education", "criminal_records"):
            for item in politician.get(section) or []:
                if not isinstance(item, dict):
                    continue
                cite = item.get("citation") or {}
                if cite.get("link") and citation_source(cite) in PRIMARY_SOURCES:
                    ref_lines.append(f"{section}: {cite['link']}")

        elections = (politician.get("political_background") or {}).get("elections") or []
        for election in elections:
            if not isinstance(election, dict):
                continue
            cite = election.get("citation") or {}
            if cite.get("link") and citation_source(cite) in PRIMARY_SOURCES:
                ref_lines.append(f"election: {cite['link']}")

        if ref_lines:
            parts.append("=== Known primary sources ===\n" + "\n".join(ref_lines))

        if fd.get("as_of_election"):
            parts.append(f"Affidavit as of election: {fd['as_of_election']}")

        return "\n\n".join(parts)

    def _log_llm_response_body(self, call_n: int, text: str) -> None:
        """Log full LLM output at INFO (on by default; disable with RAJNITI_LOG_LLM_RESPONSES=0)."""
        if not _llm_response_logging_enabled():
            return
        max_show = _llm_response_log_max_chars()
        n = len(text)
        if max_show <= 0 or n <= max_show:
            logger.info(
                "BaseAgent._run_llm call #%d RESPONSE (%d chars):\n%s",
                call_n,
                n,
                text,
            )
            return
        logger.info(
            "BaseAgent._run_llm call #%d RESPONSE (first %d of %d chars; "
            "raise RAJNITI_LLM_RESPONSE_LOG_MAX_CHARS to see more):\n%s\n... [truncated]",
            call_n,
            max_show,
            n,
            text[:max_show],
        )

    # ── LLM helpers ──────────────────────────────────────────────────────────

    @log(logger, "BaseAgent._run_llm")
    def _run_llm(self, prompt: str) -> str:
        """Send a prompt to the LLM and return plain text."""
        max_raw = (os.getenv("RAJNITI_LLM_MAX_CALLS") or "").strip()
        max_calls = int(max_raw) if max_raw else 0
        if max_calls > 0 and self._llm_call_count >= max_calls:
            raise RuntimeError(
                f"RAJNITI_LLM_MAX_CALLS ({max_calls}) exhausted for this run"
            )
        self._llm_call_count += 1
        call_n = self._llm_call_count
        logger.info(
            "BaseAgent._run_llm call #%d START prompt_chars=%d",
            call_n,
            len(prompt),
        )
        t0 = time.monotonic()
        try:
            response = self.llm.invoke(prompt)
            content = (
                response.content if hasattr(response, "content") else str(response)
            )
            if isinstance(content, list):
                content = "".join(
                    (
                        part
                        if isinstance(part, str)
                        else (
                            part.get("text", str(part))
                            if isinstance(part, dict)
                            else getattr(part, "text", str(part))
                        )
                    )
                    for part in content
                )
            text = str(content) if not isinstance(content, str) else content
            elapsed = time.monotonic() - t0
            logger.info(
                "BaseAgent._run_llm call #%d DONE elapsed_s=%.2f response_chars=%d",
                call_n,
                elapsed,
                len(text),
            )
            self._log_llm_response_body(call_n, text)
            return text
        except Exception as exc:
            elapsed = time.monotonic() - t0
            logger.warning(
                "BaseAgent._run_llm call #%d FAILED after %.2fs: %s",
                call_n,
                elapsed,
                exc,
            )
            self._record_error("llm", str(exc), exc=exc)
            raise

    @log(logger, "BaseAgent._run_llm_with_context")
    def _run_llm_with_context(self, prompt: str, context: str) -> str:
        """Prepend real-world context to the prompt, then call the LLM.

        If *context* is empty the original prompt is sent unchanged.
        """
        if not context:
            return self._run_llm(prompt)

        enriched = (
            "Use the following real-world context to provide accurate, "
            "up-to-date information. Cross-reference with your own knowledge "
            "and prefer the context when it conflicts.\n\n"
            f"{context}\n\n---\n\n{prompt}"
        )
        logger.info(
            "BaseAgent._run_llm_with_context context_chars=%d prompt_chars=%d enriched_chars=%d",
            len(context),
            len(prompt),
            len(enriched),
        )
        return self._run_llm(enriched)

    # ── JSON parsing ─────────────────────────────────────────────────────────

    @log(logger, "BaseAgent._parse_json_value")
    def _parse_json_value(self, text: str) -> Optional[Any]:
        """Extract any JSON value (object or array) from raw LLM text."""
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            pass

        starts = [idx for idx in (text.find("{"), text.find("[")) if idx != -1]
        start = min(starts) if starts else -1
        end_object = text.rfind("}") + 1
        end_array = text.rfind("]") + 1
        end = max(end_object, end_array)

        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except Exception:
                return None
        return None

    @log(logger, "BaseAgent._parse_json_object")
    def _parse_json_object(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a JSON **object** from raw text."""
        value = self._parse_json_value(text)
        return value if isinstance(value, dict) else None

    @log(logger, "BaseAgent._coerce_to_list")
    def _coerce_to_list(self, value: Any) -> Optional[list[Any]]:
        """Normalize a dict/list payload into a list."""
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return [value]
        return None

    @log(logger, "BaseAgent._validate_with_adapter")
    def _validate_with_adapter(
        self, value: Any, adapter: TypeAdapter[T]
    ) -> tuple[Optional[T], Optional[list[dict[str, Any]]]]:
        """Validate *value* against a Pydantic TypeAdapter."""
        try:
            return adapter.validate_python(value), None
        except ValidationError as exc:
            self._record_error(
                "validation",
                f"Schema validation: {len(exc.errors())} error(s)",
                exc=exc,
            )
            return None, exc.errors()
