"""Backward-compatible shim — delegates to ``free_tier_llm`` for all heavy lifting.

Existing code can keep importing from here without changes:

    from app.config.agent_config import get_agent_llm, FailoverChatLLM
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.config.free_tier_llm import (  # noqa: F401 — re-exported for backward compatibility
    DEFAULT_PROVIDERS,
    FreeTierLLM,
    ProviderConfig,
    _build_llm,
    _is_retryable,
)

logger = logging.getLogger(__name__)

# Re-export the config list so patches in existing tests still work.
PROVIDER_CONFIGS = DEFAULT_PROVIDERS

# Re-export the wrapper class under the old name for test compatibility.
FailoverChatLLM = FreeTierLLM


class AgentLLMFactory:
    """Factory that builds a FreeTierLLM from a config list (Rajniti-specific defaults)."""

    def __init__(self, config_list: Optional[list[dict[str, Any]]] = None):
        self.config_list = config_list or PROVIDER_CONFIGS

    def create(self) -> FreeTierLLM:
        return FreeTierLLM.from_env(configs=self.config_list)


def get_agent_llm() -> FreeTierLLM:
    """Drop-in accessor used by agents — unchanged signature."""
    return AgentLLMFactory().create()
