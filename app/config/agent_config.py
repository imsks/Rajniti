import os
import logging
import importlib
import time
from typing import Any, Optional, Callable

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
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "model_env": "AGENT_GEMINI_MODEL",
        "default_model": "gemini-1.5-flash",
        "base_url": None,
    },
}


def _get_model_name(llm: Any) -> str:
    """Best-effort model name extraction across providers."""
    return str(getattr(llm, "model_name", None) or getattr(llm, "model", None) or "unknown")


def _get_retry_after_seconds(exc: Exception) -> Optional[float]:
    """Best-effort extraction of retry-after seconds from provider exception."""
    retry_delay = getattr(exc, "retry_delay", None)
    if retry_delay is not None:
        seconds = getattr(retry_delay, "seconds", None)
        if isinstance(seconds, (int, float)):
            return float(seconds)
    retry_after = getattr(exc, "retry_after", None)
    if isinstance(retry_after, (int, float)):
        return float(retry_after)
    message = str(exc).lower()
    # common google message includes: "Please retry in 36.7s"
    if "retry in" in message:
        try:
            tail = message.split("retry in", 1)[1].strip()
            num = "".join(ch for ch in tail if (ch.isdigit() or ch == "."))[:10]
            return float(num) if num else None
        except Exception:
            return None
    return None


def _build_llm(provider: str) -> Optional[Any]:
    """Build a provider-specific chat LLM if API key is configured."""
    cfg = PROVIDER_CONFIGS.get(provider)
    if not cfg:
        return None

    api_key = os.getenv(cfg["api_key_env"])
    if not api_key:
        return None

    model = os.getenv(cfg["model_env"], cfg["default_model"])

    def _build_openai_compatible() -> Any:
        kwargs = dict(api_key=api_key, model=model, temperature=0)
        if cfg["base_url"]:
            kwargs["base_url"] = cfg["base_url"]
        return ChatOpenAI(**kwargs)

    def _build_gemini() -> Any:
        try:
            mod = importlib.import_module("langchain_google_genai")
            ChatGoogleGenerativeAI = getattr(mod, "ChatGoogleGenerativeAI")
        except Exception as exc:
            logger.warning("Gemini provider unavailable (missing deps): %s", exc)
            return None
        return ChatGoogleGenerativeAI(google_api_key=api_key, model=model, temperature=0)

    builders: dict[str, Callable[[], Any]] = {
        "openai": _build_openai_compatible,
        "perplexity": _build_openai_compatible,
        "gemini": _build_gemini,
    }

    builder = builders.get(provider)
    if not builder:
        return None

    built = builder()
    return built


def _is_fallback_error(exc: Exception) -> bool:
    """Return True when provider failure should trigger fallback."""
    status_code = getattr(exc, "status_code", None)
    if status_code == 429:
        return True
    if isinstance(status_code, int) and 500 <= status_code <= 599:
        return True

    # Google / Gemini quota errors
    if exc.__class__.__name__ in {"ResourceExhausted"}:
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
    if "resource_exhausted" in message:
        return True
    if "quota exceeded" in message:
        return True
    if "429" in message and "quota" in message:
        return True
    if "timeout" in message or "timed out" in message:
        return True
    if "connection error" in message or "temporary failure" in message:
        return True

    return exc.__class__.__name__ == "RateLimitError"


class FailoverChatLLM:
    """Simple runtime failover wrapper for ChatOpenAI providers."""

    def __init__(self, candidates: list[tuple[str, Any]]):
        """Store ordered provider candidates and track active model index."""
        if not candidates:
            raise ValueError("FailoverChatLLM requires at least one candidate")
        self._candidates = candidates
        self._active_index = 0
        self._cooldowns: dict[str, float] = {}

    @property
    def model_name(self) -> str:
        """Return the currently active model name."""
        return _get_model_name(self._candidates[self._active_index][1])

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """Invoke the active provider and fallback on retryable failures."""
        last_exc: Optional[Exception] = None
        now = time.time()

        for index, (provider, llm) in enumerate(self._candidates):
            until = self._cooldowns.get(provider)
            if until and until > now:
                logger.info(
                    "Agent LLM: %s in cooldown for %.1fs; skipping",
                    provider,
                    until - now,
                )
                continue
            try:
                response = llm.invoke(*args, **kwargs)
                self._active_index = index
                return response
            except Exception as exc:
                if not _is_fallback_error(exc) or index == len(self._candidates) - 1:
                    raise
                retry_after = _get_retry_after_seconds(exc)
                if retry_after:
                    self._cooldowns[provider] = time.time() + retry_after
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


class AgentLLMFactory:
    """Factory for creating a failover-enabled agent LLM."""

    def __init__(self, providers: Optional[list[str]] = None):
        """Initialize factory with explicit providers or env-based defaults."""
        self.providers = providers or self._providers_from_env()

    @staticmethod
    def _providers_from_env() -> list[str]:
        """Read and normalize provider fallback order from environment."""
        fallback_str = os.getenv("AGENT_LLM_PROVIDERS", "perplexity,openai")
        return [p.strip() for p in fallback_str.split(",") if p.strip()]

    def create(self) -> FailoverChatLLM:
        """Create a failover LLM instance from available provider clients."""
        candidates: list[tuple[str, Any]] = []

        for provider in self.providers:
            llm = _build_llm(provider)
            if llm is None:
                logger.warning("Agent LLM: %s skipped (no API key)", provider)
                continue
            logger.info("Agent LLM: candidate %s (%s)", provider, _get_model_name(llm))
            candidates.append((provider, llm))

        if candidates:
            first_provider, first_llm = candidates[0]
            logger.info("Agent LLM: using %s (%s)", first_provider, _get_model_name(first_llm))
            return FailoverChatLLM(candidates)

        raise RuntimeError(
            f"No working LLM provider found. Tried: {self.providers}. "
            "Check your API keys in .env"
        )

def get_agent_llm() -> FailoverChatLLM:
    """Backward-compatible accessor used by existing agents."""
    return AgentLLMFactory().create()
