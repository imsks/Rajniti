"""LLM access — one switch: USE_LOCAL_LLM (local LM Studio vs cloud API keys)."""

from __future__ import annotations

import os
from typing import Any, Optional

from app.config.free_tier_llm import (  # noqa: F401 — re-exported for tests
    DEFAULT_PROVIDERS,
    FreeTierLLM,
    ProviderConfig,
    _build_llm,
    _is_retryable,
)

FailoverChatLLM = FreeTierLLM
PROVIDER_CONFIGS = DEFAULT_PROVIDERS


def use_local_llm() -> bool:
    return (os.getenv("USE_LOCAL_LLM") or "false").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def llm_openai_kwargs() -> dict[str, Any]:
    """OpenAI-compatible connection params for LangChain or browser-use."""
    if use_local_llm():
        return {
            "model": os.getenv("LMSTUDIO_MODEL", "google/gemma-4-26b-a4b-qat"),
            "base_url": os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
            "api_key": os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
            "temperature": 0.1,
        }

    for cfg in DEFAULT_PROVIDERS:
        api_key = (os.getenv(cfg["api_key_env"]) or "").strip()
        if not api_key:
            continue
        kw: dict[str, Any] = {
            "model": cfg["model"],
            "api_key": api_key,
            "temperature": 0.1,
        }
        if cfg.get("base_url"):
            kw["base_url"] = cfg["base_url"]
        return kw

    raise RuntimeError(
        "No LLM configured: set USE_LOCAL_LLM=true (LM Studio) or add a cloud API key"
    )


class AgentLLMFactory:
    def __init__(self, config_list: Optional[list[dict[str, Any]]] = None):
        self.config_list = config_list or PROVIDER_CONFIGS

    def create(self) -> Any:
        if use_local_llm():
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(**llm_openai_kwargs())
        return FreeTierLLM.from_env(configs=self.config_list)


def get_agent_llm() -> Any:
    return AgentLLMFactory().create()
