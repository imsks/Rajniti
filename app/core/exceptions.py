"""
Structured exception hierarchy for Rajniti.

AgentError subclasses let the graceful-degradation layer distinguish
expected failures (LLM quota, bad JSON) from genuine bugs, so log output
stays readable even when six sub-processes fail in parallel.
"""

from __future__ import annotations


class RajnitiError(Exception):
    """Base exception for Rajniti API."""

    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AgentError(RajnitiError):
    """Base for all agent-pipeline errors."""

    category: str = "agent"

    def __init__(
        self, message: str, code: int = 500, *, cause: Exception | None = None
    ):
        super().__init__(message, code)
        self.cause = cause


class LLMError(AgentError):
    """LLM invocation failure (rate-limit, timeout, empty response)."""

    category = "llm"


class ParseError(AgentError):
    """JSON / text extraction failure from LLM output."""

    category = "parse"


class ValidationError(AgentError):
    """Pydantic schema validation failure."""

    category = "validation"


class ToolError(AgentError):
    """Agent-tool execution failure (web search, scraping, Wikipedia)."""

    category = "tool"


class NetworkError(AgentError):
    """Low-level HTTP / DNS / connection failure."""

    category = "network"
