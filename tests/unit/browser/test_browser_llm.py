"""Browser-use LLM provider routing."""

from unittest.mock import patch

import pytest
from browser_use import ChatGoogle, ChatOpenAI

from app.browser.llm import LocalBrowserChatOpenAI, build_browser_llm
from app.config.agent_config import LlmConnection, resolve_llm_connection


@pytest.mark.unit
class TestResolveLlmConnection:
    def test_gemini_uses_gemini_model_env(self, monkeypatch):
        monkeypatch.setenv("USE_LOCAL_LLM", "false")
        monkeypatch.setenv("GEMINI_API_KEY", "gem-key")
        monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-pro")

        conn = resolve_llm_connection()

        assert conn.provider == "gemini"
        assert conn.model == "gemini-2.5-pro"
        assert conn.api_key == "gem-key"
        assert conn.base_url is None

    def test_local_llm_uses_lm_studio(self, monkeypatch):
        monkeypatch.setenv("USE_LOCAL_LLM", "true")
        monkeypatch.setenv("LMSTUDIO_MODEL", "local-model")
        monkeypatch.setenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
        monkeypatch.setenv("LMSTUDIO_API_KEY", "lm-studio")

        conn = resolve_llm_connection()

        assert conn.provider == "openai"
        assert conn.model == "local-model"
        assert conn.base_url == "http://127.0.0.1:1234/v1"


@pytest.mark.unit
class TestBuildBrowserLlm:
    def test_uses_chat_google_for_gemini(self, monkeypatch):
        monkeypatch.setenv("USE_LOCAL_LLM", "false")
        conn = LlmConnection(
            provider="gemini",
            model="gemini-2.5-flash",
            api_key="gem-key",
        )

        with patch("app.browser.llm.resolve_llm_connection", return_value=conn):
            llm = build_browser_llm()

        assert isinstance(llm, ChatGoogle)
        assert llm.model == "gemini-2.5-flash"
        assert llm.api_key == "gem-key"
        assert llm.max_retries >= 1

    def test_uses_chat_openai_for_openai_compatible(self, monkeypatch):
        monkeypatch.setenv("USE_LOCAL_LLM", "false")
        conn = LlmConnection(
            provider="groq",
            model="llama-3.3-70b-versatile",
            api_key="groq-key",
            base_url="https://api.groq.com/openai/v1",
        )

        with patch("app.browser.llm.resolve_llm_connection", return_value=conn):
            llm = build_browser_llm()

        assert isinstance(llm, ChatOpenAI)
        assert llm.model == "llama-3.3-70b-versatile"
        assert llm.api_key == "groq-key"
        assert str(llm.base_url) == "https://api.groq.com/openai/v1"

    def test_uses_local_wrapper_for_lm_studio(self, monkeypatch):
        monkeypatch.setenv("USE_LOCAL_LLM", "true")
        conn = LlmConnection(
            provider="openai",
            model="local-model",
            api_key="lm-studio",
            base_url="http://127.0.0.1:1234/v1",
        )

        with patch("app.browser.llm.resolve_llm_connection", return_value=conn):
            llm = build_browser_llm()

        assert isinstance(llm, LocalBrowserChatOpenAI)
        assert llm.model == "local-model"
        assert str(llm.base_url) == "http://127.0.0.1:1234/v1"
