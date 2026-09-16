"""Makefile contract: preserve the documented developer entrypoints."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "Makefile"


def _public_targets(text: str) -> list[str]:
    return re.findall(r"^([a-zA-Z][a-zA-Z0-9_-]*):", text, re.MULTILINE)


@pytest.mark.unit
def test_makefile_exposes_expected_public_targets():
    targets = _public_targets(MAKEFILE.read_text())
    assert set(targets) == {
        "help",
        "setup",
        "install",
        "install-dev",
        "install-hooks",
        "run",
        "frontend-install",
        "frontend-dev",
        "dev",
        "dev-api",
        "dev-build",
        "stop",
        "logs",
        "prod",
        "db-migrate",
        "db-reset",
        "test",
        "lint",
        "format",
    }


@pytest.mark.unit
@pytest.mark.parametrize("target", ["setup", "dev", "dev-api", "stop"])
def test_makefile_target_dry_runs(target: str):
    result = subprocess.run(
        ["make", "-n", target],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


@pytest.mark.unit
def test_makefile_dev_api_preserves_build_zero_branch():
    text = MAKEFILE.read_text()
    assert 'if [ "$(BUILD)" = "1" ]; then \\' in text
    assert "$(COMPOSE) up postgres rajniti-api; \\" in text
