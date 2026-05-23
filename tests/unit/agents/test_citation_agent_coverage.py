"""CitationAgent coverage gate and batch accounting."""

from unittest.mock import MagicMock, patch

# IMPORTANT:
# Mock hardcoded LLM init before CitationAgent gets instantiated.
_llm_patcher = patch(
    "app.agents.base_agent.get_agent_llm",
    return_value=MagicMock(),
)
_llm_patcher.start()

from app.agents.citation_agent import CitationAgent


def _edu_politician(n_cited: int, n_slots: int, pid: str = "p1") -> dict:
    cite = {"link": "https://example.com/x", "source": "NEWS"}

    rows = []

    for i in range(n_slots):
        rows.append({"citation": cite} if i < n_cited else {})

    return {
        "id": pid,
        "name": "Test Person",
        "education": rows,
        "political_background": {
            "elections": [],
            "summary": None,
        },
    }


def test_skip_llm_when_coverage_at_threshold() -> None:

    pol = _edu_politician(10, 25)

    agent = CitationAgent()

    with patch.object(agent, "_gather_politician_context") as g:

        with patch.object(agent, "_run_llm_with_context") as llm:

            result = agent._run_for_politician(
                pol,
                force=False,
            )

    assert result["ok"] is True
    assert result.get("skipped") is True

    assert result.get("reason") == "citation_coverage_at_or_above_threshold"

    assert "coverage_pct" in result

    g.assert_not_called()
    llm.assert_not_called()


def test_force_bypasses_coverage_gate() -> None:

    pol = _edu_politician(10, 25)

    agent = CitationAgent()

    agent.politician_service = MagicMock(update_politician=MagicMock(return_value=True))

    with patch.object(
        agent,
        "_gather_politician_context",
        return_value="",
    ):

        with patch.object(
            agent,
            "_run_llm_with_context",
            return_value="{}",
        ):

            result = agent._run_for_politician(
                pol,
                force=True,
            )

    assert result.get("reason") != "citation_coverage_at_or_above_threshold"

    agent.politician_service.update_politician.assert_not_called()


def test_below_threshold_invokes_llm() -> None:

    pol = _edu_politician(9, 25)

    agent = CitationAgent()

    agent.politician_service = MagicMock(update_politician=MagicMock(return_value=True))

    with patch.object(
        agent,
        "_gather_politician_context",
        return_value="",
    ):

        with patch.object(
            agent,
            "_run_llm_with_context",
            return_value="{}",
        ) as llm:

            result = agent._run_for_politician(
                pol,
                force=False,
            )

    assert result.get("ok") is True

    llm.assert_called_once()


def test_reraise_llm_quota_when_flag_true() -> None:
    """Schedule mode relies on quota exceptions bubbling to resume after sleep."""

    pol = _edu_politician(9, 25)

    agent = CitationAgent()

    exc = RuntimeError("429 insufficient_quota")

    with patch.object(
        agent,
        "_gather_politician_context",
        return_value="",
    ):

        with patch.object(
            agent,
            "_run_llm_with_context",
            side_effect=exc,
        ):

            try:

                agent._run_for_politician(
                    pol,
                    force=False,
                    reraise_llm_quota=True,
                )

            except RuntimeError as e:

                assert e is exc

                return

    raise AssertionError("expected reraised quota exception")


def test_batch_passes_force_through_to_fully_cited() -> None:

    cite = {
        "link": "https://example.com/x",
        "source": "NEWS",
    }

    fully = {
        "id": "done1",
        "name": "Fully Cited",
        "education": [
            {
                "qualification": "B",
                "citation": cite,
            }
        ],
        "political_background": {
            "elections": [],
            "summary": None,
        },
    }

    svc = MagicMock()

    svc.get_all_politicians.return_value = [fully]

    agent = CitationAgent()

    agent.politician_service = svc

    with patch.object(
        agent,
        "_gather_politician_context",
        return_value="",
    ):

        with patch.object(
            agent,
            "_run_llm_with_context",
            return_value="{}",
        ) as llm:

            summary = agent._run_all(force=False)

    assert summary["skipped"] == 1
    assert summary["processed"] == 0

    llm.assert_not_called()

    with patch.object(
        agent,
        "_gather_politician_context",
        return_value="",
    ):

        with patch.object(
            agent,
            "_run_llm_with_context",
            return_value="{}",
        ) as llm:

            summary = agent._run_all(force=True)

    assert summary["processed"] == 0

    assert summary["skipped"] == 1

    llm.assert_called_once()


def test_batch_classifies_internal_skips_separately() -> None:

    pol = _edu_politician(
        10,
        25,
        pid="gap1",
    )

    svc = MagicMock()

    svc.get_all_politicians.return_value = [pol]

    agent = CitationAgent()

    agent.politician_service = svc

    summary = agent._run_all(force=False)

    assert summary["skipped"] == 1

    assert summary["processed"] == 0
