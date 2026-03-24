"""Unit tests for LLM provider failover configuration and per-model cooldown.

Tests target the backward-compatible shim (agent_config) which delegates
to the new FreeTierLLM wrapper — guaranteeing zero breakage for downstream code.
"""

from unittest.mock import Mock, patch

import pytest

from app.config.agent_config import FailoverChatLLM, get_agent_llm

_TEST_CONFIG = [
    {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
    },
    {
        "provider": "perplexity",
        "model": "sonar",
        "api_key_env": "PERPLEXITY_API_KEY",
        "base_url": "https://api.perplexity.ai",
    },
]


class FakeRateLimitError(Exception):
    """Test double to simulate provider 429/insufficient quota."""

    status_code = 429
    code = "insufficient_quota"


class FakeAuthError(Exception):
    """Test double for non-retryable authentication errors."""

    status_code = 401


@pytest.mark.unit
class TestAgentConfigFailover:
    """Tests runtime fallback behavior for agent LLM (multi-model, per-model cooldown)."""

    def test_returns_first_provider_when_invoke_succeeds(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "tk")
        monkeypatch.setenv("PERPLEXITY_API_KEY", "tk")

        primary = Mock()
        primary.model_name = "gpt-4o-mini"
        response = Mock(content="Narendra Modi")
        primary.invoke.return_value = response

        secondary = Mock()
        secondary.model_name = "sonar"

        with (
            patch("app.config.agent_config.PROVIDER_CONFIGS", _TEST_CONFIG),
            patch(
                "app.config.free_tier_llm._build_llm", side_effect=[primary, secondary]
            ),
        ):
            llm = get_agent_llm()
            result = llm.invoke("Who is PM of India?")

        assert isinstance(llm, FailoverChatLLM)
        assert result.content == "Narendra Modi"
        assert llm.model_name == "gpt-4o-mini"
        primary.invoke.assert_called_once()
        secondary.invoke.assert_not_called()

    def test_falls_back_on_rate_limit_error(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "tk")
        monkeypatch.setenv("PERPLEXITY_API_KEY", "tk")

        primary = Mock()
        primary.model_name = "gpt-4o-mini"
        primary.invoke.side_effect = FakeRateLimitError("insufficient quota")

        secondary = Mock()
        secondary.model_name = "sonar"
        response = Mock(content="Narendra Modi")
        secondary.invoke.return_value = response

        with (
            patch("app.config.agent_config.PROVIDER_CONFIGS", _TEST_CONFIG),
            patch(
                "app.config.free_tier_llm._build_llm", side_effect=[primary, secondary]
            ),
        ):
            llm = get_agent_llm()
            result = llm.invoke("Who is PM of India?")

        assert result.content == "Narendra Modi"
        assert llm.model_name == "sonar"
        primary.invoke.assert_called_once()
        secondary.invoke.assert_called_once()

    def test_does_not_fallback_on_non_retryable_error(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "tk")
        monkeypatch.setenv("PERPLEXITY_API_KEY", "tk")

        primary = Mock()
        primary.model_name = "gpt-4o-mini"
        primary.invoke.side_effect = FakeAuthError("unauthorized")

        secondary = Mock()
        secondary.model_name = "sonar"

        with (
            patch("app.config.agent_config.PROVIDER_CONFIGS", _TEST_CONFIG),
            patch(
                "app.config.free_tier_llm._build_llm", side_effect=[primary, secondary]
            ),
        ):
            llm = get_agent_llm()
            with pytest.raises(FakeAuthError, match="unauthorized"):
                llm.invoke("Who is PM of India?")

        primary.invoke.assert_called_once()
        secondary.invoke.assert_not_called()

    def test_raises_when_no_provider_has_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        with (
            patch("app.config.agent_config.PROVIDER_CONFIGS", _TEST_CONFIG),
            patch("app.config.free_tier_llm._build_llm", return_value=None),
        ):
            with pytest.raises(RuntimeError, match="no working providers"):
                get_agent_llm()

    def test_per_model_cooldown_skips_rate_limited_model_then_uses_next(self):
        """Per-model cooldown: first model rate-limited with retry_after; next call skips it."""
        primary = Mock()
        secondary = Mock()
        response = Mock(content="ok")
        secondary.invoke.return_value = response

        class FakeWithRetry(FakeRateLimitError):
            retry_after = 2.0

        primary.invoke.side_effect = FakeWithRetry("quota")

        candidates = [
            ("gemini", "gemini-1.5-flash", primary),
            ("gemini", "gemini-2.0-flash", secondary),
        ]
        llm = FailoverChatLLM(candidates)

        result = llm.invoke("Hi")
        assert result.content == "ok"
        primary.invoke.assert_called_once()
        secondary.invoke.assert_called_once()

        # Next call: first model still in cooldown, so skip to second
        secondary.invoke.reset_mock()
        primary.invoke.reset_mock()
        primary.invoke.return_value = Mock(content="from-primary")
        result2 = llm.invoke("Hi again")
        assert result2.content == "ok"
        primary.invoke.assert_not_called()
        assert secondary.invoke.call_count == 1

    def test_failover_exhausts_all_then_raises_last_exception(self):
        """When all candidates fail with fallback errors, last exception is raised."""
        m1 = Mock()
        m1.invoke.side_effect = FakeRateLimitError("limit 1")
        m2 = Mock()
        m2.invoke.side_effect = FakeRateLimitError("limit 2")

        candidates = [
            ("openai", "gpt-4o-mini", m1),
            ("perplexity", "sonar", m2),
        ]
        llm = FailoverChatLLM(candidates)

        with pytest.raises(FakeRateLimitError, match="limit 2"):
            llm.invoke("Hi")

        m1.invoke.assert_called_once()
        m2.invoke.assert_called_once()
