"""BaseAgent LLM call logging (timing and payload sizes)."""

import logging
from unittest.mock import Mock, patch

import pytest

from app.agents.base_agent import BaseAgent


@pytest.fixture
def agent_with_mock_llm():
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="ok-response")
    with patch("app.agents.base_agent.get_agent_llm", return_value=mock_llm):
        agent = BaseAgent()
    return agent, mock_llm


def test_run_llm_logs_start_done_and_chars(caplog, agent_with_mock_llm) -> None:
    caplog.set_level(logging.INFO)
    agent, mock_llm = agent_with_mock_llm
    text = agent._run_llm("abcdef")
    assert text == "ok-response"
    mock_llm.invoke.assert_called_once()
    joined = "\n".join(r.message for r in caplog.records)
    assert "START prompt_chars=6" in joined
    assert "DONE" in joined
    assert "response_chars=" in joined
    assert "RESPONSE (11 chars):" in joined or "RESPONSE" in joined
    assert "ok-response" in joined


def test_run_llm_skips_response_body_when_disabled(caplog, monkeypatch) -> None:
    monkeypatch.setenv("RAJNITI_LOG_LLM_RESPONSES", "0")
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="secret-body")
    with patch("app.agents.base_agent.get_agent_llm", return_value=mock_llm):
        agent = BaseAgent()
    caplog.set_level(logging.INFO)
    agent._run_llm("x")
    joined = "\n".join(r.message for r in caplog.records)
    assert "secret-body" not in joined


def test_run_llm_with_context_logs_sizes(caplog, agent_with_mock_llm) -> None:
    caplog.set_level(logging.INFO)
    agent, _ = agent_with_mock_llm
    agent._run_llm_with_context("prompt-only", "ctx-block")
    joined = " ".join(r.message for r in caplog.records)
    assert "context_chars=9" in joined
    assert "prompt_chars=11" in joined
    assert "enriched_chars=" in joined
