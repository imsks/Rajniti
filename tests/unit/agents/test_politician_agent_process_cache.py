from app.agents.politician_agent import PoliticianAgent


class _DummyCache:
    def __init__(self) -> None:
        self._store: dict[str, object] = {}

    def set(self, key: str, value: object) -> None:
        self._store[key] = value

    def exists(self, key: str) -> bool:
        return key in self._store


class _DummyService:
    def __init__(self) -> None:
        self.update_calls: list[tuple[str, dict]] = []

    def get_by_id(self, politician_id: str) -> dict:
        out: dict = {"id": politician_id, "name": "Test", "criminal_records": []}
        for pid, upd in self.update_calls:
            if pid == politician_id:
                out = {**out, **upd}
        return out

    def update_politician(self, politician_id: str, updates: dict):
        self.update_calls.append((politician_id, updates))
        return {"id": politician_id, **updates}


class _DummyProcess:
    name = "criminal_records"

    def __init__(self) -> None:
        self.run_calls = 0

    def should_run(self, politician, force: bool = False) -> bool:
        return force or not politician.get("criminal_records")

    def run(self, politician, force: bool = False, context: str = ""):
        self.run_calls += 1
        return {
            "process": self.name,
            "ok": True,
            "skipped": False,
            "updates": {"criminal_records": []},
        }


def _build_agent_for_test() -> tuple[PoliticianAgent, _DummyProcess, _DummyService]:
    agent = PoliticianAgent.__new__(PoliticianAgent)
    process = _DummyProcess()
    service = _DummyService()
    agent.processes = [process]
    agent.politician_service = service
    agent.source_orchestrator = type("O", (), {"sync_politician": lambda *a, **k: {"ok": True, "sources_run": []}})()
    agent.citation_agent = type(
        "C",
        (),
        {"_run_for_politician": lambda *a, **k: {"ok": True, "skipped": True}},
    )()
    agent.cache = _DummyCache()
    agent._errors = []
    agent._gather_politician_context = lambda politician: ""
    return agent, process, service


def test_process_cached_after_empty_update() -> None:
    agent, process, service = _build_agent_for_test()
    politician = {"id": "p1", "name": "Test", "criminal_records": []}

    first = agent._run_for_politician(
        politician, force=False, skip_sources=True, skip_citations=True
    )
    second = agent._run_for_politician(
        politician, force=False, skip_sources=True, skip_citations=True
    )

    assert first["ok"] is True
    assert second["ok"] is True
    assert process.run_calls == 1
    assert len(service.update_calls) == 1
    assert any(
        r.get("process") == "criminal_records" and r.get("reason") == "cached_processed"
        for r in second["process_results"]
    )
