"""USE_LOCAL_LLM switch."""

import os
from unittest.mock import patch

import pytest

from app.config.agent_config import AgentLLMFactory, get_agent_llm, use_local_llm


@pytest.mark.unit
def test_use_local_llm_env() -> None:
    with patch.dict(os.environ, {"USE_LOCAL_LLM": "true"}):
        assert use_local_llm() is True
    with patch.dict(os.environ, {"USE_LOCAL_LLM": "false"}):
        assert use_local_llm() is False


@pytest.mark.unit
def test_agent_factory_uses_local_when_flag_set(monkeypatch) -> None:
    monkeypatch.setenv("USE_LOCAL_LLM", "true")
    monkeypatch.setenv("LMSTUDIO_MODEL", "test-model")
    llm = AgentLLMFactory().create()
    assert hasattr(llm, "invoke")
    assert llm.model_name == "test-model"
