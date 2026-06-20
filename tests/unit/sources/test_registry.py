"""Source registry tests."""

import pytest

from app.sources.registry import list_sources


def test_list_sources_empty_without_names() -> None:
    assert list_sources() == []
    assert list_sources(names=None) == []


def test_list_sources_loads_on_demand() -> None:
    modules = list_sources(names=["myneta"])
    assert len(modules) == 1
    assert modules[0].NAME == "myneta"


def test_list_sources_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown source"):
        list_sources(names=["not_a_source"])
