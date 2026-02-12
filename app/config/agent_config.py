import os
import logging
from typing import Any, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

logger = logging.getLogger(__name__)

PROVIDER_CONFIGS = {
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "model_env": "AGENT_OPENAI_MODEL",
        "default_model": "gpt-4o-mini",
        "base_url": None,
    },
    "perplexity": {
        "api_key_env": "PERPLEXITY_API_KEY",
        "model_env": "AGENT_PERPLEXITY_MODEL",
        "default_model": "sonar",
        "base_url": "https://api.perplexity.ai",
    },
}


def _build_llm(provider: str) -> Optional[ChatOpenAI]:
    cfg = PROVIDER_CONFIGS.get(provider)
    if not cfg:
        return None

    api_key = os.getenv(cfg["api_key_env"])
    if not api_key:
        return None

    model = os.getenv(cfg["model_env"], cfg["default_model"])

    kwargs = dict(api_key=api_key, model=model, temperature=0)
    if cfg["base_url"]:
        kwargs["base_url"] = cfg["base_url"]

    return ChatOpenAI(**kwargs)


def _is_fallback_error(exc: Exception) -> bool:
    """Return True when provider failure should trigger fallback."""
    status_code = getattr(exc, "status_code", None)
    if status_code == 429:
        return True

    code = getattr(exc, "code", None)
    if code in {"insufficient_quota", "rate_limit_exceeded"}:
        return True

    error_attr = getattr(exc, "error", None)
    if isinstance(error_attr, dict):
        nested_code = error_attr.get("code")
        if nested_code in {"insufficient_quota", "rate_limit_exceeded"}:
            return True

    message = str(exc).lower()
    if "insufficient_quota" in message or "rate limit" in message:
        return True

    return exc.__class__.__name__ == "RateLimitError"


class FailoverChatLLM:
    """Simple runtime failover wrapper for ChatOpenAI providers."""

    def __init__(self, candidates: list[tuple[str, ChatOpenAI]]):
        if not candidates:
            raise ValueError("FailoverChatLLM requires at least one candidate")
        self._candidates = candidates
        self._active_index = 0

    @property
    def model_name(self) -> str:
        return self._candidates[self._active_index][1].model_name

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        last_exc: Optional[Exception] = None

        for index, (provider, llm) in enumerate(self._candidates):
            try:
                response = llm.invoke(*args, **kwargs)
                self._active_index = index
                return response
            except Exception as exc:
                if not _is_fallback_error(exc) or index == len(self._candidates) - 1:
                    raise
                logger.warning(
                    "Agent LLM: %s failed (%s). Falling back...",
                    provider,
                    exc.__class__.__name__,
                )
                last_exc = exc

        if last_exc:
            raise last_exc
        raise RuntimeError("Agent LLM invocation failed without a captured exception")

    def __getattr__(self, item: str) -> Any:
        """Delegate unknown attributes to currently active provider."""
        return getattr(self._candidates[self._active_index][1], item)


def get_agent_llm() -> FailoverChatLLM:
    fallback_str = os.getenv("AGENT_LLM_PROVIDERS", "perplexity,openai")
    providers = [p.strip() for p in fallback_str.split(",") if p.strip()]
    candidates: list[tuple[str, ChatOpenAI]] = []

    for provider in providers:
        llm = _build_llm(provider)
        if llm is None:
            logger.warning("Agent LLM: %s skipped (no API key)", provider)
            continue
        logger.info("Agent LLM: candidate %s (%s)", provider, llm.model_name)
        candidates.append((provider, llm))

    if candidates:
        first_provider, first_llm = candidates[0]
        logger.info("Agent LLM: using %s (%s)", first_provider, first_llm.model_name)
        return FailoverChatLLM(candidates)

    raise RuntimeError(
        f"No working LLM provider found. Tried: {providers}. "
        "Check your API keys in .env"
    )
