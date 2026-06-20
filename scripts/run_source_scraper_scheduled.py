"""Scheduled runner for source scraper with checkpoint + sleep."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core import setup_logging

logger = logging.getLogger(__name__)

_SCRAPER = Path(__file__).resolve().parent / "scrape_politician_sources.py"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run source scraper on a schedule")
    parser.add_argument("--type", choices=["MP", "MLA"], default=None)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--source", action="append", required=True)
    parser.add_argument("--schedule-sleep-seconds", type=float, default=3600.0)
    parser.add_argument("--checkpoint-file", type=Path, default=None)
    parser.add_argument("--reset-checkpoint", action="store_true")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    args = parser.parse_args()
    setup_logging(args.log_level)

    while True:
        cmd = [
            sys.executable,
            str(_SCRAPER),
            "--log-level",
            args.log_level,
            "--limit",
            str(args.limit),
        ]
        if args.type:
            cmd.extend(["--type", args.type])
        if args.force:
            cmd.append("--force")
        for src in args.source or []:
            cmd.extend(["--source", src])
        if args.checkpoint_file:
            cmd.extend(["--checkpoint-file", str(args.checkpoint_file)])
        if args.reset_checkpoint:
            cmd.append("--reset-checkpoint")
            args.reset_checkpoint = False

        logger.info("Running source scraper: %s", " ".join(cmd))
        proc = subprocess.run(cmd, cwd=str(_SCRAPER.parent.parent))
        if proc.returncode != 0:
            logger.warning("Source scraper exited with code %s", proc.returncode)

        logger.info("Sleeping %.0fs before next wave", args.schedule_sleep_seconds)
        time.sleep(args.schedule_sleep_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
