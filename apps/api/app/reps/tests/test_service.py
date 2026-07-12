import pytest

from app.reps import Representative, RepsService


@pytest.mark.unit
def test_get_representative_returns_dto() -> None:
    rep = RepsService().get_representative("mp-123")

    assert isinstance(rep, Representative)
    assert rep.id == "mp-123"
