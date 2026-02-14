"""Unit tests for LLM provider failover configuration."""

from unittest.mock import Mock, patch

import pytest

from app.config.agent_config import FailoverChatLLM, get_agent_llm


class FakeRateLimitError(Exception):
    """Test double to simulate provider 429/insufficient quota."""

    status_code = 429
    code = "insufficient_quota"


@pytest.mark.unit
class TestAgentConfigFailover:
    """Tests runtime fallback behavior for agent LLM."""

    def test_returns_first_provider_when_invoke_succeeds(self, monkeypatch):
        monkeypatch.setenv("AGENT_LLM_PROVIDERS", "openai,perplexity")

        primary = Mock()
        primary.model_name = "gpt-4o-mini"
        response = Mock(content="Narendra Modi")
        primary.invoke.return_value = response

        secondary = Mock()
        secondary.model_name = "sonar"

        with patch(
            "app.config.agent_config._build_llm",
            side_effect=[primary, secondary],
        ):
            llm = get_agent_llm()
            result = llm.invoke("Who is PM of India?")

        assert isinstance(llm, FailoverChatLLM)
        assert result.content == "Narendra Modi"
        assert llm.model_name == "gpt-4o-mini"
        primary.invoke.assert_called_once()
        secondary.invoke.assert_not_called()

    def test_falls_back_on_rate_limit_error(self, monkeypatch):
        monkeypatch.setenv("AGENT_LLM_PROVIDERS", "openai,perplexity")

        primary = Mock()
        primary.model_name = "gpt-4o-mini"
        primary.invoke.side_effect = FakeRateLimitError("insufficient quota")

        secondary = Mock()
        secondary.model_name = "sonar"
        response = Mock(content="Narendra Modi")
        secondary.invoke.return_value = response

        with patch(
            "app.config.agent_config._build_llm",
            side_effect=[primary, secondary],
        ):
            llm = get_agent_llm()
            result = llm.invoke("Who is PM of India?")

        assert result.content == "Narendra Modi"
        assert llm.model_name == "sonar"
        primary.invoke.assert_called_once()
        secondary.invoke.assert_called_once()

    def test_does_not_fallback_on_non_retryable_error(self, monkeypatch):
        monkeypatch.setenv("AGENT_LLM_PROVIDERS", "openai,perplexity")

        primary = Mock()
        primary.model_name = "gpt-4o-mini"
        primary.invoke.side_effect = ValueError("bad prompt")

        secondary = Mock()
        secondary.model_name = "sonar"

        with patch(
            "app.config.agent_config._build_llm",
            side_effect=[primary, secondary],
        ):
            llm = get_agent_llm()
            with pytest.raises(ValueError, match="bad prompt"):
                llm.invoke("Who is PM of India?")

        primary.invoke.assert_called_once()
        secondary.invoke.assert_not_called()

    def test_raises_when_no_provider_has_api_key(self, monkeypatch):
        monkeypatch.setenv("AGENT_LLM_PROVIDERS", "openai,perplexity")

        with patch("app.config.agent_config._build_llm", return_value=None):
            with pytest.raises(RuntimeError, match="No working LLM provider found"):
                get_agent_llm()
