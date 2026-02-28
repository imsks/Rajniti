import importlib
import logging
import os
import time
from typing import Any, Callable, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Flat list: fallback order is top to bottom. Exhaust models of one provider, then next.
# API keys stay in .env; model names are configured here.
PROVIDER_CONFIGS = [
    # Gemini (try in order)
    {"provider": "gemini", "model": "gemini-3.1-pro-preview", "api_key_env": "GEMINI_API_KEY"},
    {"provider": "gemini", "model": "gemini-3-pro-preview", "api_key_env": "GEMINI_API_KEY"},
    {"provider": "gemini", "model": "gemini-3-flash-preview", "api_key_env": "GEMINI_API_KEY"},
    {"provider": "gemini", "model": "gemini-2.5-flash", "api_key_env": "GEMINI_API_KEY"},
    # OpenAI (try in order)
    {"provider": "openai", "model": "gpt-4o-mini", "api_key_env": "OPENAI_API_KEY", "base_url": None},
    {"provider": "openai", "model": "gpt-4o", "api_key_env": "OPENAI_API_KEY", "base_url": None},
    # Perplexity
    {"provider": "perplexity", "model": "sonar", "api_key_env": "PERPLEXITY_API_KEY", "base_url": "https://api.perplexity.ai"},
]


def _get_model_name(llm: Any) -> str:
    """Best-effort model name extraction across providers."""
    return str(
        getattr(llm, "model_name", None) or getattr(llm, "model", None) or "unknown"
    )


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


def _build_llm(
    provider: str,
    model: str,
    api_key: str,
    base_url: Optional[str] = None,
) -> Optional[Any]:
    """Build a provider-specific chat LLM with explicit model name and API key."""
    if not model or not api_key:
        return None

    def _build_openai_compatible() -> Any:
        try:
            mod = importlib.import_module("langchain_openai")
            ChatOpenAI = getattr(mod, "ChatOpenAI")
        except Exception as exc:
            logger.warning("OpenAI provider unavailable (missing deps): %s", exc)
            return None
        kwargs: dict[str, Any] = dict(api_key=api_key, model=model, temperature=0)
        if base_url:
            kwargs["base_url"] = base_url
        return ChatOpenAI(**kwargs)

    def _build_gemini() -> Any:
        try:
            mod = importlib.import_module("langchain_google_genai")
            ChatGoogleGenerativeAI = getattr(mod, "ChatGoogleGenerativeAI")
        except Exception as exc:
            logger.warning("Gemini provider unavailable (missing deps): %s", exc)
            return None
        return ChatGoogleGenerativeAI(
            google_api_key=api_key, model=model, temperature=0
        )

    builders: dict[str, Callable[[], Any]] = {
        "openai": _build_openai_compatible,
        "perplexity": _build_openai_compatible,
        "gemini": _build_gemini,
    }

    builder = builders.get(provider)
    if not builder:
        return None

    return builder()


def _is_fallback_error(exc: Exception) -> bool:
    """Return True when provider failure should trigger fallback."""
    status_code = getattr(exc, "status_code", None)
    if status_code == 429:
        return True
    if isinstance(status_code, int) and 500 <= status_code <= 599:
        return True

    # Google / Gemini quota and API errors
    if exc.__class__.__name__ in {"ResourceExhausted", "GoogleAPIError"}:
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
    """Runtime failover wrapper: tries candidates in order with per-model cooldown on rate limit."""

    def __init__(self, candidates: list[tuple[str, str, Any]]):
        """Store ordered (provider, model, llm) candidates and per-model cooldowns."""
        if not candidates:
            raise ValueError("FailoverChatLLM requires at least one candidate")
        self._candidates = candidates
        self._active_index = 0
        self._cooldowns: dict[tuple[str, str], float] = {}

    @property
    def model_name(self) -> str:
        """Return the currently active model name."""
        _provider, model, llm = self._candidates[self._active_index]
        return model

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """Invoke candidates in order; on retryable failure, cooldown this model and try next."""
        last_exc: Optional[Exception] = None
        now = time.time()

        for index, (provider, model, llm) in enumerate(self._candidates):
            key = (provider, model)
            until = self._cooldowns.get(key)
            if until and until > now:
                logger.info(
                    "Agent LLM: %s/%s in cooldown for %.1fs; skipping",
                    provider,
                    model,
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
                    self._cooldowns[key] = time.time() + retry_after
                logger.warning(
                    "Agent LLM: %s/%s failed (%s). Falling back...",
                    provider,
                    model,
                    exc.__class__.__name__,
                )
                last_exc = exc

        if last_exc:
            raise last_exc
        raise RuntimeError("Agent LLM invocation failed without a captured exception")

    def __getattr__(self, item: str) -> Any:
        """Delegate unknown attributes to currently active provider."""
        return getattr(self._candidates[self._active_index][2], item)


class AgentLLMFactory:
    """Factory for creating a failover-enabled agent LLM from PROVIDER_CONFIGS."""

    def __init__(self, config_list: Optional[list[dict[str, Any]]] = None):
        """Initialize with explicit config or default PROVIDER_CONFIGS."""
        self.config_list = config_list or PROVIDER_CONFIGS

    def create(self) -> FailoverChatLLM:
        """Build all configured models with valid API keys; return failover LLM."""
        candidates: list[tuple[str, str, Any]] = []

        for cfg in self.config_list:
            provider = cfg["provider"]
            model = cfg["model"]
            api_key_env = cfg["api_key_env"]
            base_url = cfg.get("base_url")

            api_key = os.getenv(api_key_env)
            if not api_key:
                logger.warning(
                    "Agent LLM: %s/%s skipped (no %s in .env)",
                    provider,
                    model,
                    api_key_env,
                )
                continue

            llm = _build_llm(provider, model, api_key, base_url)
            if llm is None:
                logger.warning("Agent LLM: %s/%s build failed", provider, model)
                continue

            logger.info("Agent LLM: candidate %s/%s", provider, model)
            candidates.append((provider, model, llm))

        if candidates:
            first_provider, first_model, _ = candidates[0]
            logger.info("Agent LLM: using %s/%s", first_provider, first_model)
            return FailoverChatLLM(candidates)

        raise RuntimeError(
            "No working LLM provider found. Check your API keys in .env"
        )


def get_agent_llm() -> FailoverChatLLM:
    """Backward-compatible accessor used by existing agents."""
    return AgentLLMFactory().create()
