import pytest

from app.agents import AgentResult, AgentsService, AgentTask


@pytest.mark.unit
def test_run_returns_result_for_task() -> None:
    service = AgentsService()

    result = service.run(AgentTask(kind="promise_check", prompt="Did X keep Y?"))

    assert isinstance(result, AgentResult)
    assert result.task_kind == "promise_check"
    assert "promise_check" in result.answer
