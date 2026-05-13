"""CLI smoke tests for runnable Wikipedia context script."""

import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_run_wikipedia_context_help_exits_zero() -> None:
    root = _repo_root()
    script = root / "scripts" / "run_wikipedia_context.py"
    r = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(root),
    )
    assert r.returncode == 0
    out = r.stdout.lower()
    assert "wikipedia" in out
