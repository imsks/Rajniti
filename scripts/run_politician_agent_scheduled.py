#!/usr/bin/env python3
"""Politician agent runner with checkpointing and optional LLM invocation caps.

For long batches: resumes from `.cache/agent_schedule_checkpoint.json`.
Exits with code 0 when stopping due to API quota exhaustion so schedulers treat
quota stops as success (not hard failure).

Environment:
    RAJNITI_LLM_MAX_CALLS — optional cap on LLM invocations per process (BaseAgent).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.politician_agent import PoliticianAgent, _is_llm_quota_exc
from app.core import setup_logging
from app.services.politician_service import PoliticianService

logger = logging.getLogger(__name__)

_DEFAULT_CHECKPOINT = Path(__file__).resolve().parents[1] / ".cache" / "agent_schedule_checkpoint.json"


def _load_checkpoint(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"last_id": None, "last_index": -1}
    try:
        with path.open("r", encoding="utf-8") as f:
            return {**{"last_id": None, "last_index": -1}, **json.load(f)}
    except Exception:
        return {"last_id": None, "last_index": -1}


def _save_checkpoint(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run PoliticianAgent over a list with checkpointing. "
            "Stops with exit 0 if LLM providers are exhausted."
        )
    )
    parser.add_argument(
        "--type",
        choices=["MP", "MLA"],
        default=None,
        help="Only politicians of this election type",
    )
    parser.add_argument(
        "--max-politicians",
        type=int,
        default=0,
        help="Max rows to process this run (0 = no limit)",
    )
    parser.add_argument(
        "--checkpoint-file",
        type=Path,
        default=_DEFAULT_CHECKPOINT,
        help="JSON checkpoint path for resume",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.0,
        help="Pause between politicians (rate limiting)",
    )
    parser.add_argument(
        "--reset-checkpoint",
        action="store_true",
        help="Start from beginning; clears checkpoint before run",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--source",
        action="append",
        help="External source to sync before enrichment (repeatable), e.g. myneta",
    )
    parser.add_argument(
        "--skip-sources",
        action="store_true",
        help="Skip browser source sync (default runs myneta)",
    )
    parser.add_argument(
        "--skip-citations",
        action="store_true",
        help="Skip citation backfill after LLM enrichment (on by default)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    args = parser.parse_args()

    setup_logging(args.log_level)

    if args.reset_checkpoint:
        if args.checkpoint_file.exists():
            args.checkpoint_file.unlink()

    service = PoliticianService()
    if args.type in ("MP", "MLA"):
        politicians: List[Dict[str, Any]] = service.get_all(args.type)
    else:
        politicians = service.get_all_politicians()

    cp = _load_checkpoint(args.checkpoint_file)
    start_idx = int(cp.get("last_index", -1)) + 1
    last_id = cp.get("last_id")

    if last_id and start_idx > 0:
        # Resume: find index after last_id if list shifted
        id_list = [str(p.get("id")) for p in politicians]
        if last_id in id_list:
            start_idx = id_list.index(last_id) + 1

    agent = PoliticianAgent()
    processed = 0
    stopped_quota = False

    for idx in range(start_idx, len(politicians)):
        if args.max_politicians and processed >= args.max_politicians:
            logger.info("Reached --max-politicians=%s", args.max_politicians)
            break

        p = politicians[idx]
        pid = p.get("id")
        if not pid:
            continue

        logger.info(
            "Scheduled run [%d/%d] id=%s name=%s",
            idx + 1,
            len(politicians),
            pid,
            p.get("name"),
        )

        try:
            result = agent._run_for_politician(
                p,
                force=args.force,
                source_names=args.source,
                skip_sources=args.skip_sources,
                skip_citations=args.skip_citations,
            )
        except Exception as exc:
            if _is_llm_quota_exc(exc):
                logger.warning(
                    "Stopping scheduled run due to LLM limit / quota: %s", exc
                )
                stopped_quota = True
                _save_checkpoint(
                    args.checkpoint_file,
                    {"last_id": str(pid), "last_index": idx - 1},
                )
                break
            logger.exception("Politician run failed: %s", exc)
            _save_checkpoint(
                args.checkpoint_file,
                {"last_id": str(pid), "last_index": idx},
            )
            raise

        _save_checkpoint(
            args.checkpoint_file,
            {"last_id": str(pid), "last_index": idx},
        )
        processed += 1
        if not result.get("ok"):
            logger.warning("Non-OK result for %s: %s", pid, result)

        if args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)

    if stopped_quota:
        print(
            json.dumps(
                {
                    "status": "stopped_llm_quota",
                    "processed_this_run": processed,
                    "checkpoint": str(args.checkpoint_file),
                },
                indent=2,
            )
        )
        raise SystemExit(0)

    print(
        json.dumps(
            {
                "status": "completed",
                "processed_this_run": processed,
                "checkpoint": str(args.checkpoint_file),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
