"""LLM access — one switch: USE_LOCAL_LLM (local LM Studio vs cloud API keys)."""

from __future__ import annotations

import os
from dataclasses import dataclass
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


_MODEL_ENV_BY_PROVIDER: dict[str, str] = {
    "gemini": "GEMINI_MODEL",
    "openai": "AGENT_OPENAI_MODEL",
    "perplexity": "AGENT_PERPLEXITY_MODEL",
}


@dataclass(frozen=True)
class LlmConnection:
    provider: str
    model: str
    api_key: str
    base_url: str | None = None
    temperature: float = 0.1


def _model_for_provider(provider: str, default_model: str) -> str:
    env_name = _MODEL_ENV_BY_PROVIDER.get(provider)
    if not env_name:
        return default_model
    return (os.getenv(env_name) or default_model).strip() or default_model


def resolve_llm_connection() -> LlmConnection:
    """Active LLM provider + credentials (first configured cloud provider, or LM Studio)."""
    if use_local_llm():
        return LlmConnection(
            provider="openai",
            model=os.getenv("LMSTUDIO_MODEL", "google/gemma-4-26b-a4b-qat"),
            api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
            base_url=os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
        )

    for cfg in DEFAULT_PROVIDERS:
        api_key = (os.getenv(cfg["api_key_env"]) or "").strip()
        if not api_key:
            continue
        return LlmConnection(
            provider=cfg["provider"],
            model=_model_for_provider(cfg["provider"], cfg["model"]),
            api_key=api_key,
            base_url=cfg.get("base_url"),
        )

    raise RuntimeError(
        "No LLM configured: set USE_LOCAL_LLM=true (LM Studio) or add a cloud API key"
    )


def llm_openai_kwargs() -> dict[str, Any]:
    """OpenAI-compatible connection params for LangChain or browser-use."""
    conn = resolve_llm_connection()
    kw: dict[str, Any] = {
        "model": conn.model,
        "api_key": conn.api_key,
        "temperature": conn.temperature,
    }
    if conn.base_url:
        kw["base_url"] = conn.base_url
    return kw


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
