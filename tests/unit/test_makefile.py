"""Makefile contract: only setup, up, and stop."""

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
def test_makefile_exposes_only_setup_up_stop():
    targets = _public_targets(MAKEFILE.read_text())
    assert targets == ["setup", "up", "stop"]


@pytest.mark.unit
@pytest.mark.parametrize("target", ["setup", "up", "stop"])
def test_makefile_target_dry_runs(target: str):
    result = subprocess.run(
        ["make", "-n", target],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
