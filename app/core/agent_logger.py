"""
Structured agentic logging for Rajniti agents.

Provides high-visibility logging for:
- LLM calls (provider, model, prompt, response, timing)
- Tool invocations (tool name, input, output, timing)
- Agent step transitions (what the agent decided and why)
- State transitions (LangGraph node changes)
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Generator, Optional


class AgentLogger:
    """Structured logger for agent operations.

    Wraps a standard logger with agent-specific formatting methods.
    All methods respect the underlying logger's level.
    """

    def __init__(self, name: str) -> None:
        self._logger = logging.getLogger(name)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    # ── LLM Call Logging ─────────────────────────────────────────────────────

    def llm_call_start(
        self,
        *,
        call_id: int,
        provider: str,
        model: str,
        prompt_chars: int,
        prompt_preview: str = "",
        timeout_secs: Optional[float] = None,
    ) -> None:
        """Log the start of an LLM invocation."""
        timeout_str = f" timeout={timeout_secs}s" if timeout_secs else ""
        self._logger.info(
            "[LLM] call #%d START → %s/%s | prompt=%d chars%s",
            call_id,
            provider,
            model,
            prompt_chars,
            timeout_str,
        )
        if prompt_preview:
            self._logger.debug(
                "[LLM] call #%d prompt_preview: %.200s",
                call_id,
                prompt_preview.replace("\n", " "),
            )

    def llm_call_success(
        self,
        *,
        call_id: int,
        provider: str,
        model: str,
        response_chars: int,
        elapsed_s: float,
        response_preview: str = "",
    ) -> None:
        """Log a successful LLM response."""
        self._logger.info(
            "[LLM] call #%d DONE ✓ %s/%s | response=%d chars | %.2fs",
            call_id,
            provider,
            model,
            response_chars,
            elapsed_s,
        )
        if response_preview:
            self._logger.debug(
                "[LLM] call #%d response_preview: %.300s",
                call_id,
                response_preview.replace("\n", " "),
            )

    def llm_call_failed(
        self,
        *,
        call_id: int,
        provider: str,
        model: str,
        elapsed_s: float,
        error: str,
        error_class: str = "",
        will_retry: bool = False,
        retry_num: int = 0,
        max_retries: int = 0,
    ) -> None:
        """Log a failed LLM call."""
        retry_info = ""
        if will_retry:
            retry_info = f" | WILL RETRY ({retry_num}/{max_retries})"
        self._logger.error(
            "[LLM] call #%d FAILED ✗ %s/%s | %.2fs | %s: %s%s",
            call_id,
            provider,
            model,
            elapsed_s,
            error_class or "Error",
            error[:200],
            retry_info,
        )

    # ── Tool Call Logging ────────────────────────────────────────────────────

    def tool_call(
        self,
        *,
        tool: str,
        action: str,
        input_preview: str = "",
        output_preview: str = "",
        elapsed_s: float = 0.0,
        success: bool = True,
    ) -> None:
        """Log a tool invocation (web search, scraper, wikipedia, etc.)."""
        status = "✓" if success else "✗"
        self._logger.info(
            "[TOOL] %s %s.%s | %.2fs%s",
            status,
            tool,
            action,
            elapsed_s,
            f" | input={input_preview[:100]}" if input_preview else "",
        )
        if output_preview:
            self._logger.debug(
                "[TOOL] %s output: %.200s",
                tool,
                output_preview.replace("\n", " "),
            )

    # ── Agent Step Logging ───────────────────────────────────────────────────

    def step(
        self,
        step_name: str,
        action: str,
        *,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an agent decision/action step."""
        detail_str = ""
        if details:
            parts = [f"{k}={v}" for k, v in details.items()]
            detail_str = f" | {', '.join(parts)}"
        self._logger.info("[STEP] %s → %s%s", step_name, action, detail_str)

    def step_skip(
        self,
        step_name: str,
        reason: str,
    ) -> None:
        """Log that a step was skipped."""
        self._logger.info("[STEP] %s → SKIPPED (%s)", step_name, reason)

    def step_complete(
        self,
        step_name: str,
        result_summary: str,
        *,
        elapsed_s: float = 0.0,
    ) -> None:
        """Log step completion with result."""
        self._logger.info(
            "[STEP] %s → DONE (%s) | %.2fs", step_name, result_summary, elapsed_s
        )

    # ── State Transition Logging (LangGraph) ─────────────────────────────────

    def state_transition(
        self,
        from_node: str,
        to_node: str,
        *,
        reason: str = "",
    ) -> None:
        """Log a LangGraph node transition."""
        reason_str = f" ({reason})" if reason else ""
        self._logger.info(
            "[GRAPH] %s → %s%s", from_node, to_node, reason_str
        )

    # ── Data/Gap Analysis Logging ────────────────────────────────────────────

    def data_status(
        self,
        entity: str,
        *,
        existing: int = 0,
        expected: int = 0,
        missing: int = 0,
        action: str = "",
    ) -> None:
        """Log data availability analysis."""
        self._logger.info(
            "[DATA] %s | existing=%d expected=%d missing=%d%s",
            entity,
            existing,
            expected,
            missing,
            f" → {action}" if action else "",
        )

    # ── Retry Logging ────────────────────────────────────────────────────────

    def retry(
        self,
        operation: str,
        *,
        attempt: int,
        max_attempts: int,
        wait_s: float,
        error: str = "",
    ) -> None:
        """Log a retry attempt."""
        self._logger.warning(
            "[RETRY] %s | attempt %d/%d | waiting %.1fs%s",
            operation,
            attempt,
            max_attempts,
            wait_s,
            f" | last_error: {error[:100]}" if error else "",
        )

    # ── Context Manager for Timed Operations ─────────────────────────────────

    @contextmanager
    def timed_operation(
        self, operation: str, **details: Any
    ) -> Generator[dict[str, Any], None, None]:
        """Context manager that logs start/end with timing.

        Usage:
            with alog.timed_operation("fetch_bucket", bucket="A-D") as ctx:
                result = do_work()
                ctx["result_count"] = len(result)
        """
        detail_str = " | ".join(f"{k}={v}" for k, v in details.items())
        self._logger.info(
            "[OP] START %s%s", operation, f" | {detail_str}" if detail_str else ""
        )
        ctx: dict[str, Any] = {}
        t0 = time.perf_counter()
        try:
            yield ctx
            elapsed = time.perf_counter() - t0
            result_str = " | ".join(f"{k}={v}" for k, v in ctx.items())
            self._logger.info(
                "[OP] DONE %s | %.2fs%s",
                operation,
                elapsed,
                f" | {result_str}" if result_str else "",
            )
        except Exception as exc:
            elapsed = time.perf_counter() - t0
            self._logger.error(
                "[OP] FAILED %s | %.2fs | %s: %s",
                operation,
                elapsed,
                type(exc).__name__,
                str(exc)[:200],
            )
            raise
