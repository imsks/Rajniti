"""Tests for the portable FreeTierLLM wrapper (session exhaustion, status, reset)."""

from unittest.mock import Mock, patch

import pytest

from app.config.free_tier_llm import FreeTierLLM, ProviderConfig, _build_llm

# -- helpers ----------------------------------------------------------------


class FakeRateLimitError(Exception):
    status_code = 429
    code = "insufficient_quota"


class FakeQuotaExhausted(Exception):
    """Simulates a daily-quota-exceeded error with no retry hint."""

    status_code = 429

    def __str__(self):
        return "Resource exhausted: daily quota used up"


class FakeGoogleResourceExhausted(Exception):
    """Simulates google.api_core.exceptions.ResourceExhausted which has .code (int), not .status_code."""

    code = 429

    def __str__(self):
        return "429 You exceeded your current quota, please check your plan and billing details."


class FakeQuotaWithLongRetry(Exception):
    """Simulates quota exceeded with a long retry-after (> 5 min)."""

    status_code = 429
    retry_after = 600.0

    def __str__(self):
        return "Quota exceeded, retry in 600s"


def _make_candidates(*names: str) -> list[tuple[str, str, Mock]]:
    mocks = []
    for name in names:
        m = Mock()
        m.model_name = name
        mocks.append(("test", name, m))
    return mocks


# -- tests ------------------------------------------------------------------


@pytest.mark.unit
class TestFreeTierLLMFallback:

    def test_first_candidate_succeeds(self):
        cands = _make_candidates("m1", "m2")
        cands[0][2].invoke.return_value = Mock(content="hello")
        llm = FreeTierLLM(cands)

        result = llm.invoke("hi")
        assert result.content == "hello"
        assert llm.model_name == "m1"
        cands[1][2].invoke.assert_not_called()

    def test_falls_through_on_retryable_error(self):
        cands = _make_candidates("m1", "m2")
        cands[0][2].invoke.side_effect = FakeRateLimitError("rate limit")
        cands[1][2].invoke.return_value = Mock(content="from m2")
        llm = FreeTierLLM(cands)

        result = llm.invoke("hi")
        assert result.content == "from m2"
        assert llm.model_name == "m2"

    def test_non_retryable_error_raises_immediately(self):
        """Auth errors (401) must not trigger fallback."""

        class FakeAuthError(Exception):
            status_code = 401

        cands = _make_candidates("m1", "m2")
        cands[0][2].invoke.side_effect = FakeAuthError("unauthorized")
        llm = FreeTierLLM(cands)

        with pytest.raises(FakeAuthError, match="unauthorized"):
            llm.invoke("hi")
        cands[1][2].invoke.assert_not_called()

    def test_plain_python_error_does_not_fallback(self):
        """Plain Python exceptions (no status_code) are not retried across models."""
        cands = _make_candidates("m1", "m2")
        cands[0][2].invoke.side_effect = ValueError("bad input")
        llm = FreeTierLLM(cands)

        with pytest.raises(ValueError, match="bad input"):
            llm.invoke("hi")
        cands[1][2].invoke.assert_not_called()

    def test_google_resource_exhausted_triggers_fallback(self):
        """Google API exceptions have .code (int) not .status_code — must still fallback."""
        cands = _make_candidates("m1", "m2")
        cands[0][2].invoke.side_effect = FakeGoogleResourceExhausted()
        cands[1][2].invoke.return_value = Mock(content="from m2")
        llm = FreeTierLLM(cands)

        result = llm.invoke("hi")
        assert result.content == "from m2"
        assert llm.model_name == "m2"
        cands[0][2].invoke.assert_called_once()
        cands[1][2].invoke.assert_called_once()

    def test_raises_last_error_when_all_fail(self):
        cands = _make_candidates("m1", "m2")
        cands[0][2].invoke.side_effect = FakeRateLimitError("err1")
        cands[1][2].invoke.side_effect = FakeRateLimitError("err2")
        llm = FreeTierLLM(cands)

        with pytest.raises(FakeRateLimitError, match="err2"):
            llm.invoke("hi")


@pytest.mark.unit
class TestFreeTierLLMSessionExhaustion:

    def test_quota_exhausted_marks_model_for_session(self):
        """A quota error with no retry hint marks the model exhausted for the whole session."""
        cands = _make_candidates("m1", "m2")
        cands[0][2].invoke.side_effect = FakeQuotaExhausted()
        cands[1][2].invoke.return_value = Mock(content="fallback")
        llm = FreeTierLLM(cands)

        llm.invoke("hi")
        assert ("test", "m1") in llm._session_exhausted

        # Second call should skip m1 entirely
        cands[0][2].invoke.reset_mock()
        cands[0][2].invoke.return_value = Mock(content="would succeed")
        cands[1][2].invoke.reset_mock()
        cands[1][2].invoke.return_value = Mock(content="still fallback")

        result = llm.invoke("second call")
        assert result.content == "still fallback"
        cands[0][2].invoke.assert_not_called()

    def test_long_retry_after_marks_session_exhausted(self):
        """A quota error with retry_after > 300s marks the model exhausted for the session."""
        cands = _make_candidates("m1", "m2")
        cands[0][2].invoke.side_effect = FakeQuotaWithLongRetry()
        cands[1][2].invoke.return_value = Mock(content="ok")
        llm = FreeTierLLM(cands)

        llm.invoke("hi")
        assert ("test", "m1") in llm._session_exhausted

    def test_reset_session_clears_exhaustion(self):
        cands = _make_candidates("m1", "m2")
        cands[0][2].invoke.side_effect = FakeQuotaExhausted()
        cands[1][2].invoke.return_value = Mock(content="ok")
        llm = FreeTierLLM(cands)

        llm.invoke("first")
        assert ("test", "m1") in llm._session_exhausted

        llm.reset_session()
        assert len(llm._session_exhausted) == 0
        assert len(llm._cooldowns) == 0


@pytest.mark.unit
class TestFreeTierLLMStatus:

    def test_status_returns_all_models(self):
        cands = _make_candidates("m1", "m2", "m3")
        for _, _, m in cands:
            m.invoke.return_value = Mock(content="x")
        llm = FreeTierLLM(cands)

        s = llm.status()
        assert len(s["models"]) == 3
        assert all(m["state"] == "available" for m in s["models"])

    def test_status_shows_exhausted(self):
        cands = _make_candidates("m1", "m2")
        cands[0][2].invoke.side_effect = FakeQuotaExhausted()
        cands[1][2].invoke.return_value = Mock(content="ok")
        llm = FreeTierLLM(cands)

        llm.invoke("hi")
        s = llm.status()
        assert s["models"][0]["state"] == "exhausted"
        assert s["models"][1]["state"] == "available"

    def test_status_shows_cooldown(self):
        cands = _make_candidates("m1", "m2")
        cands[0][2].invoke.side_effect = FakeRateLimitError("rate limit")
        cands[1][2].invoke.return_value = Mock(content="ok")
        llm = FreeTierLLM(cands)

        llm.invoke("hi")
        s = llm.status()
        assert s["models"][0]["state"].startswith("cooldown")


@pytest.mark.unit
class TestFreeTierLLMFactory:

    def test_from_env_skips_missing_keys(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "tk")

        test_configs = [
            {
                "provider": "gemini",
                "model": "gemini-2.5-flash",
                "api_key_env": "GEMINI_API_KEY",
            },
            {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "api_key_env": "OPENAI_API_KEY",
            },
        ]

        fake_llm = Mock()
        with patch("app.config.free_tier_llm._build_llm", return_value=fake_llm):
            llm = FreeTierLLM.from_env(configs=test_configs)

        assert llm.candidate_count == 1
        assert llm.model_name == "gpt-4o-mini"

    def test_from_env_raises_when_none_available(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        test_configs = [
            {"provider": "gemini", "model": "x", "api_key_env": "GEMINI_API_KEY"},
        ]

        with pytest.raises(RuntimeError, match="no working providers"):
            FreeTierLLM.from_env(configs=test_configs)

    def test_from_env_free_only_flag(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "tk")
        monkeypatch.setenv("OPENAI_API_KEY", "tk")

        test_configs = [
            {
                "provider": "gemini",
                "model": "flash",
                "api_key_env": "GEMINI_API_KEY",
                "tier": "free",
            },
            {
                "provider": "openai",
                "model": "gpt-4o",
                "api_key_env": "OPENAI_API_KEY",
                "tier": "paid",
            },
        ]

        fake_llm = Mock()
        with patch("app.config.free_tier_llm._build_llm", return_value=fake_llm):
            llm = FreeTierLLM.from_env(configs=test_configs, free_only=True)

        assert llm.candidate_count == 1
        assert llm.model_name == "flash"


@pytest.mark.unit
class TestProviderConfig:

    def test_from_dict_minimal(self):
        cfg = ProviderConfig.from_dict(
            {
                "provider": "gemini",
                "model": "gemini-2.5-flash",
                "api_key_env": "GEMINI_API_KEY",
            }
        )
        assert cfg.provider == "gemini"
        assert cfg.tier == "free"
        assert cfg.tags == ()

    def test_from_dict_full(self):
        cfg = ProviderConfig.from_dict(
            {
                "provider": "openai",
                "model": "gpt-4o",
                "api_key_env": "OPENAI_API_KEY",
                "base_url": "https://custom.api",
                "tier": "paid",
                "tags": ["fallback", "expensive"],
            }
        )
        assert cfg.base_url == "https://custom.api"
        assert cfg.tier == "paid"
        assert cfg.tags == ("fallback", "expensive")


@pytest.mark.unit
class TestBuildLLMTimeouts:

    def test_openai_compatible_includes_request_timeout(self):
        captured = {}

        class DummyChatOpenAI:
            def __init__(self, **kwargs):
                captured.update(kwargs)

        class DummyModule:
            ChatOpenAI = DummyChatOpenAI

        with patch("importlib.import_module", return_value=DummyModule()):
            llm = _build_llm(
                "groq", "llama-3.3-70b-versatile", "k", "https://api.groq.com/openai/v1"
            )

        assert llm is not None
        assert "request_timeout" in captured
        assert captured["request_timeout"] > 0

    def test_gemini_includes_timeout(self):
        captured = {}

        class DummyChatGoogleGenerativeAI:
            def __init__(self, **kwargs):
                captured.update(kwargs)

        class DummyModule:
            ChatGoogleGenerativeAI = DummyChatGoogleGenerativeAI

        with patch("importlib.import_module", return_value=DummyModule()):
            llm = _build_llm("gemini", "gemini-3-flash-preview", "k")

        assert llm is not None
        assert "timeout" in captured
        assert captured["timeout"] > 0
