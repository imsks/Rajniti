"""Source orchestrator tests."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.sources.base import SourceResult
from app.sources.merge import SOURCE_PRIORITY
from app.sources.orchestrator import SourceOrchestrator


def test_orchestrator_persists_merged_data(monkeypatch) -> None:
    service = MagicMock()
    orch = SourceOrchestrator(politician_service=service)

    politician = {
        "id": "abc",
        "name": "Test",
        "state": "Bihar",
        "constituency": "AC",
        "type": "MLA",
        "political_background": {"elections": []},
    }

    fake_data = {
        "financial_disclosure": {
            "total_assets_inr": 100,
            "citation": {
                "link": "https://myneta.info/x",
                "source": "MYNETA",
            },
        },
        "source_sync": {"myneta": "2026-01-01T00:00:00Z"},
    }

    fake_mod = SimpleNamespace(
        NAME="fake",
        PRIORITY=SOURCE_PRIORITY["myneta"],
        can_fetch=lambda p, force=False: True,
        fetch=lambda p, force=False: SourceResult(
            source_name="fake", data=fake_data, priority=SOURCE_PRIORITY["myneta"]
        ),
    )

    monkeypatch.setattr(
        "app.sources.orchestrator.list_sources",
        lambda names=None: [fake_mod],
    )

    result = orch.sync_politician(politician, force=True)
    assert result["ok"] is True
    service.update_politician.assert_called_once()
