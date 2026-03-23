"""
free_tier_llm — Portable LangChain-first wrapper that rotates through
free-tier LLM providers with automatic fallback and session-level cooldown.

Drop this single file into any Python project. Dependencies:
  - python-dotenv
  - langchain-openai        (for OpenAI-compatible providers)
  - langchain-google-genai  (for Gemini)

Usage:
    from free_tier_llm import FreeTierLLM

    llm = FreeTierLLM.from_env()       # uses DEFAULT_PROVIDERS
    response = llm.invoke("Hello!")     # auto-fallback on quota errors

    # Or bring your own config:
    llm = FreeTierLLM.from_env(configs=[
        {"provider": "gemini", "model": "gemini-2.5-flash", "api_key_env": "GEMINI_API_KEY"},
    ])
"""

from __future__ import annotations

import importlib
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _float_env(name: str, default: float) -> float:
    """Read a positive float from env, else fallback to default."""
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
        return value if value > 0 else default
    except Exception:
        return default


# Hard timeout per candidate call so failover cannot stall indefinitely.
_REQUEST_TIMEOUT_SECS = _float_env("FREE_TIER_LLM_TIMEOUT_SECS", 15.0)

# ---------------------------------------------------------------------------
# 1. Provider config schema
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderConfig:
    """One model slot in the fallback chain.

    Only ``provider``, ``model``, and ``api_key_env`` are required.
    Everything else has sensible defaults.
    """

    provider: str
    model: str
    api_key_env: str
    base_url: Optional[str] = None
    tier: str = "free"
    tags: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ProviderConfig:
        tags = d.get("tags", ())
        if isinstance(tags, list):
            tags = tuple(tags)
        return cls(
            provider=d["provider"],
            model=d["model"],
            api_key_env=d["api_key_env"],
            base_url=d.get("base_url"),
            tier=d.get("tier", "free"),
            tags=tags,
        )


# ---------------------------------------------------------------------------
# 2. Default free-tier model list (priority = top to bottom)
# ---------------------------------------------------------------------------

DEFAULT_PROVIDERS: list[dict[str, Any]] = [
    # --- Gemini (generous free tier) ---
    {
        "provider": "gemini",
        "model": "gemini-3.1-pro-preview",
        "api_key_env": "GEMINI_API_KEY",
    },
    {
        "provider": "gemini",
        "model": "gemini-3-flash-preview",
        "api_key_env": "GEMINI_API_KEY",
    },
    {"provider": "gemini", "model": "gemini-2.5-pro", "api_key_env": "GEMINI_API_KEY"},

    {"provider": "gemini", "model": "gemini-3-flash", "api_key_env": "GEMINI_API_KEY"},
    {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "api_key_env": "GEMINI_API_KEY",
    },
    {
        "provider": "gemini",
        "model": "gemini-2.0-flash",
        "api_key_env": "GEMINI_API_KEY",
    },

    {"provider": "gemini", "model": "gemini-2.5-flash", "api_key_env": "GEMINI_API_KEY"},
    {"provider": "gemini", "model": "gemini-2.0-flash", "api_key_env": "GEMINI_API_KEY"},

    # --- Groq (ultra-fast free inference) ---
    {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
    },
    {
        "provider": "groq",
        "model": "llama-3.1-8b-instant",
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
    },
    {
        "provider": "groq",
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
    },
    {
        "provider": "groq",
        "model": "qwen/qwen3-32b",
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
    },
    {
        "provider": "groq",
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
    },
    {
        "provider": "groq",
        "model": "openai/gpt-oss-safeguard-20b",
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
    },
    # --- Mistral (1B tokens/month free) ---
    {
        "provider": "mistral",
        "model": "codestral-latest",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    {
        "provider": "mistral",
        "model": "open-mistral-7b",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    {
        "provider": "mistral",
        "model": "open-mixtral-8x22b",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    {
        "provider": "mistral",
        "model": "mistral-large-2512",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    {
        "provider": "mistral",
        "model": "open-mistral-nemo-2407",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    {
        "provider": "mistral",
        "model": "mistral-medium-2508",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    {
        "provider": "mistral",
        "model": "mistral-small-2506",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    {
        "provider": "mistral",
        "model": "ministral-14b-2512",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    {
        "provider": "mistral",
        "model": "ministral-8b-2512",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    {
        "provider": "mistral",
        "model": "ministral-3b-2512",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    {
        "provider": "mistral",
        "model": "magistral-medium-2509",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    {
        "provider": "mistral",
        "model": "magistral-small-2509",
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    # --- OpenRouter (access to many free models) ---
    {
        "provider": "openrouter",
        "model": "google/gemini-2.0-flash-exp:free",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
    },
    # --- Paid fallbacks (safety net) ---
    {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
        "tier": "paid",
    },
    {
        "provider": "perplexity",
        "model": "sonar",
        "api_key_env": "PERPLEXITY_API_KEY",
        "base_url": "https://api.perplexity.ai",
        "tier": "paid",
    },
]


# ---------------------------------------------------------------------------
# 3. Provider builders (LangChain adapters)
# ---------------------------------------------------------------------------


def _build_llm(
    provider: str,
    model: str,
    api_key: str,
    base_url: Optional[str] = None,
) -> Optional[Any]:
    """Build a LangChain chat model for the given provider."""
    if not model or not api_key:
        return None

    def _openai_compatible() -> Any:
        try:
            mod = importlib.import_module("langchain_openai")
            ChatOpenAI = getattr(mod, "ChatOpenAI")
        except Exception as exc:
            logger.warning("OpenAI-compatible provider unavailable: %s", exc)
            return None
        kwargs: dict[str, Any] = dict(
            api_key=api_key,
            model=model,
            temperature=0,
            max_retries=0,  # our wrapper handles fallback — no internal retries
            request_timeout=_REQUEST_TIMEOUT_SECS,
        )
        if base_url:
            kwargs["base_url"] = base_url
        return ChatOpenAI(**kwargs)

    def _gemini() -> Any:
        try:
            mod = importlib.import_module("langchain_google_genai")
            ChatGoogleGenerativeAI = getattr(mod, "ChatGoogleGenerativeAI")
        except Exception as exc:
            logger.warning("Gemini provider unavailable: %s", exc)
            return None
        return ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model,
            temperature=0,
            max_retries=0,  # our wrapper handles fallback — no internal retries
            timeout=_REQUEST_TIMEOUT_SECS,
        )

    _BUILDERS: dict[str, Callable[[], Any]] = {
        "gemini": _gemini,
        "openai": _openai_compatible,
        "groq": _openai_compatible,
        "mistral": _openai_compatible,
        "openrouter": _openai_compatible,
        "perplexity": _openai_compatible,
        "deepseek": _openai_compatible,
        "together": _openai_compatible,
        "fireworks": _openai_compatible,
    }

    builder = _BUILDERS.get(provider)
    if builder is None:
        logger.warning("Unknown provider %r — trying OpenAI-compatible", provider)
        builder = _openai_compatible

    return builder()


# ---------------------------------------------------------------------------
# 4. Error classification
# ---------------------------------------------------------------------------


def _get_retry_after_seconds(exc: Exception) -> Optional[float]:
    """Best-effort extraction of retry-after seconds from provider exceptions."""
    retry_delay = getattr(exc, "retry_delay", None)
    if retry_delay is not None:
        seconds = getattr(retry_delay, "seconds", None)
        if isinstance(seconds, (int, float)):
            return float(seconds)

    retry_after = getattr(exc, "retry_after", None)
    if isinstance(retry_after, (int, float)):
        return float(retry_after)

    message = str(exc).lower()
    if "retry in" in message:
        try:
            tail = message.split("retry in", 1)[1].strip()
            num = "".join(ch for ch in tail if (ch.isdigit() or ch == "."))[:10]
            return float(num) if num else None
        except Exception:
            return None
    return None


def _is_retryable(exc: Exception) -> bool:
    """Return True when this error should trigger fallback to the next model."""
    exc_str = str(exc)
    class_name = exc.__class__.__name__
    status_code = getattr(exc, "status_code", None)
    code = getattr(exc, "code", None)

    # Google API exceptions (ResourceExhausted, etc.) expose HTTP status via
    # .code (int) rather than .status_code.  Normalize so all downstream
    # checks work uniformly.
    if status_code is None and isinstance(code, int):
        status_code = code

    logger.error(
        "FreeTierLLM error — class=%s status=%s code=%s msg=%s",
        class_name,
        status_code,
        code,
        exc_str[:300],
    )

    # Auth errors: cannot fix by switching models of *same* provider key
    if status_code in {401, 403}:
        return False
    if class_name in {"AuthenticationError", "PermissionDenied", "Unauthorized"}:
        return False

    # Model/config errors — failover to the next candidate so that
    # a single bad model entry (wrong name, invalid deadline, etc.)
    # does not block the entire chain.
    if status_code == 404:
        return True
    if status_code == 400:
        msg = exc_str.lower()
        if "invalid" in msg and "quota" not in msg and "rate" not in msg:
            return True

    # Known retryable HTTP status codes (rate-limit, server errors)
    if status_code in {429, 500, 502, 503, 504, 529}:
        return True

    # Exceptions without any status code: check class name and message for
    # known retryable patterns before defaulting to non-retryable.
    if status_code is None:
        name_lower = class_name.lower()
        if any(
            kw in name_lower
            for kw in (
                "timeout",
                "connection",
                "network",
                "dns",
                "resourceexhausted",
                "ratelimit",
                "toomanyrequests",
                "serviceunavailable",
                "internalserver",
            )
        ):
            return True
        msg_lower = exc_str.lower()
        if any(
            kw in msg_lower
            for kw in (
                "timeout",
                "connection refused",
                "unreachable",
                "429",
                "quota",
                "rate limit",
                "resource exhausted",
                "too many requests",
                "capacity",
                "overloaded",
            )
        ):
            return True
        return False

    return True


# ---------------------------------------------------------------------------
# 5. Session-aware failover wrapper
# ---------------------------------------------------------------------------

_ModelKey = tuple[str, str]  # (provider, model)

_DEFAULT_COOLDOWN_SECS = 60.0
_SESSION_EXHAUST_COOLDOWN_SECS = 3600.0


class FreeTierLLM:
    """Failover LLM that rotates through free-tier models in priority order.

    On each ``.invoke()`` call the wrapper walks the candidate list top-down,
    skipping any model that is in cooldown (rate-limited) or marked exhausted
    for this session (daily quota hit).  When a model succeeds it becomes the
    *active* model for attribute delegation (``model_name``, ``bind_tools``, etc.).
    """

    def __init__(self, candidates: list[tuple[str, str, Any]]) -> None:
        if not candidates:
            raise ValueError("FreeTierLLM requires at least one candidate")
        self._candidates = candidates
        self._active_index = 0

        # (provider, model) -> unix-timestamp until which the model is on cooldown
        self._cooldowns: dict[_ModelKey, float] = {}

        # models exhausted for the entire session (quota fully consumed)
        self._session_exhausted: set[_ModelKey] = set()

    # -- public helpers -----------------------------------------------------

    @property
    def model_name(self) -> str:
        _, model, _ = self._candidates[self._active_index]
        return model

    @property
    def active_provider(self) -> str:
        provider, _, _ = self._candidates[self._active_index]
        return provider

    @property
    def candidate_count(self) -> int:
        return len(self._candidates)

    def status(self) -> dict[str, Any]:
        """Return a human-friendly status snapshot."""
        now = time.time()
        models = []
        for provider, model, _ in self._candidates:
            key = (provider, model)
            state = "available"
            if key in self._session_exhausted:
                state = "exhausted"
            elif key in self._cooldowns and self._cooldowns[key] > now:
                state = f"cooldown ({self._cooldowns[key] - now:.0f}s)"
            models.append({"provider": provider, "model": model, "state": state})
        return {"active": self.model_name, "models": models}

    def reset_session(self) -> None:
        """Clear all cooldowns and exhaustion flags (e.g. on a new day)."""
        self._cooldowns.clear()
        self._session_exhausted.clear()
        self._active_index = 0

    # -- core invocation ----------------------------------------------------

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """Try candidates top-down; cool-down / exhaust failed ones; raise if all fail."""
        last_exc: Optional[Exception] = None
        now = time.time()

        for idx, (provider, model, llm) in enumerate(self._candidates):
            key: _ModelKey = (provider, model)

            if key in self._session_exhausted:
                logger.debug(
                    "FreeTierLLM: %s/%s exhausted for session, skip", provider, model
                )
                continue

            cooldown_until = self._cooldowns.get(key)
            if cooldown_until and cooldown_until > now:
                logger.debug(
                    "FreeTierLLM: %s/%s cooldown %.0fs, skip",
                    provider,
                    model,
                    cooldown_until - now,
                )
                continue

            logger.info(
                "FreeTierLLM: trying %s/%s (%d/%d)",
                provider,
                model,
                idx + 1,
                len(self._candidates),
            )

            try:
                response = llm.invoke(*args, **kwargs)
                self._active_index = idx
                logger.info("FreeTierLLM: SUCCESS with %s/%s", provider, model)
                return response
            except Exception as exc:
                if not _is_retryable(exc):
                    raise

                retry_after = _get_retry_after_seconds(exc)
                self._apply_cooldown(key, exc, retry_after)
                last_exc = exc

                remaining = len(self._candidates) - idx - 1
                if remaining == 0:
                    raise
                logger.warning(
                    "FreeTierLLM: %s/%s failed (%s), %d candidates remain",
                    provider,
                    model,
                    exc.__class__.__name__,
                    remaining,
                )

        if last_exc:
            raise last_exc
        raise RuntimeError("FreeTierLLM: all candidates skipped or failed")

    # -- cooldown internals -------------------------------------------------

    def _apply_cooldown(
        self,
        key: _ModelKey,
        exc: Exception,
        retry_after: Optional[float],
    ) -> None:
        """Set cooldown or mark model as session-exhausted based on error signals."""
        msg = str(exc).lower()
        is_quota_exhausted = any(
            kw in msg
            for kw in ("quota", "resource exhausted", "daily limit", "exceeded")
        )

        if is_quota_exhausted and retry_after and retry_after > 300:
            self._session_exhausted.add(key)
            logger.warning(
                "FreeTierLLM: %s/%s marked EXHAUSTED for session (retry_after=%.0fs)",
                key[0],
                key[1],
                retry_after,
            )
            return

        if is_quota_exhausted and not retry_after:
            self._session_exhausted.add(key)
            logger.warning(
                "FreeTierLLM: %s/%s marked EXHAUSTED for session (quota error, no retry hint)",
                key[0],
                key[1],
            )
            return

        duration = retry_after if retry_after else _DEFAULT_COOLDOWN_SECS
        self._cooldowns[key] = time.time() + duration
        logger.info(
            "FreeTierLLM: %s/%s cooldown for %.0fs",
            key[0],
            key[1],
            duration,
        )

    # -- attribute proxy to active LLM --------------------------------------

    def __getattr__(self, item: str) -> Any:
        return getattr(self._candidates[self._active_index][2], item)

    def __repr__(self) -> str:
        return (
            f"<FreeTierLLM active={self.model_name} "
            f"candidates={self.candidate_count}>"
        )

    # -- factory ------------------------------------------------------------

    @classmethod
    def from_env(
        cls,
        configs: Optional[Sequence[dict[str, Any]]] = None,
        *,
        free_only: bool = False,
    ) -> FreeTierLLM:
        """Build from env vars.  Pass ``free_only=True`` to skip paid fallbacks."""
        raw_configs = list(configs or DEFAULT_PROVIDERS)

        candidates: list[tuple[str, str, Any]] = []
        for raw in raw_configs:
            cfg = ProviderConfig.from_dict(raw) if isinstance(raw, dict) else raw

            if free_only and cfg.tier != "free":
                continue

            api_key = (os.getenv(cfg.api_key_env) or "").strip()
            if not api_key:
                logger.warning(
                    "FreeTierLLM: skip %s/%s (no %s)",
                    cfg.provider,
                    cfg.model,
                    cfg.api_key_env,
                )
                continue

            llm = _build_llm(cfg.provider, cfg.model, api_key, cfg.base_url)
            if llm is None:
                logger.warning(
                    "FreeTierLLM: skip %s/%s (build failed)", cfg.provider, cfg.model
                )
                continue

            logger.info(
                "FreeTierLLM: registered %s/%s [%s]", cfg.provider, cfg.model, cfg.tier
            )
            candidates.append((cfg.provider, cfg.model, llm))

        if not candidates:
            raise RuntimeError(
                "FreeTierLLM: no working providers. "
                "Set at least one API key (GEMINI_API_KEY, GROQ_API_KEY, etc.) in .env"
            )

        return cls(candidates)
