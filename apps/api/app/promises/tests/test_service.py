import pytest

from app.promises import Promise, PromisesService


@pytest.mark.unit
def test_list_promises_returns_list() -> None:
    promises = PromisesService().list_promises("mp-123")

    assert isinstance(promises, list)
    assert all(isinstance(p, Promise) for p in promises)
