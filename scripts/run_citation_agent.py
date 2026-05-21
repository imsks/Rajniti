"""CLI for citation-only backfill (use PoliticianAgent for fact enrichment)."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.citation_agent import CitationAgent
from app.agents.politician_agent import _is_llm_quota_exc
from app.core import setup_logging

logger = logging.getLogger(__name__)

_DEFAULT_CKPT = (
    Path(__file__).resolve().parents[1] / ".cache" / "citation_schedule_checkpoint.json"
)


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


def _run_schedule(agent: CitationAgent, args: argparse.Namespace) -> None:
    service = agent.politician_service
    ckpt_path: Path = args.checkpoint_file

    if args.reset_checkpoint and ckpt_path.exists():
        ckpt_path.unlink()

    while True:
        if args.type in ("MP", "MLA"):
            politicians: List[Dict[str, Any]] = service.get_all(args.type)
        else:
            politicians = service.get_all_politicians()

        if args.limit and args.limit > 0:
            politicians = politicians[: args.limit]

        cp = _load_checkpoint(ckpt_path)
        start_idx = int(cp.get("last_index", -1)) + 1
        last_id = cp.get("last_id")

        if last_id and start_idx > 0:
            id_list = [str(p.get("id")) for p in politicians if p.get("id")]
            if last_id in id_list:
                start_idx = id_list.index(last_id) + 1

        quota_hit = False
        processed_wave = 0

        for idx in range(start_idx, len(politicians)):
            p = politicians[idx]
            pid = p.get("id")
            if not pid:
                continue

            logger.info(
                "Citation schedule [%d/%d] id=%s name=%s",
                idx + 1,
                len(politicians),
                pid,
                p.get("name"),
            )

            try:
                result = agent._run_for_politician(
                    p, force=args.force, reraise_llm_quota=True
                )
            except Exception as exc:
                if _is_llm_quota_exc(exc):
                    logger.warning(
                        "Citation schedule: quota / limit hit, sleeping %.0fs: %s",
                        args.schedule_sleep_seconds,
                        exc,
                    )
                    _save_checkpoint(
                        ckpt_path,
                        {"last_id": str(pid), "last_index": idx - 1},
                    )
                    quota_hit = True
                    break
                raise

            _save_checkpoint(ckpt_path, {"last_id": str(pid), "last_index": idx})
            if result.get("ok") and not result.get("skipped"):
                processed_wave += 1

            if args.sleep_seconds > 0:
                time.sleep(args.sleep_seconds)

        if quota_hit:
            time.sleep(args.schedule_sleep_seconds)
            continue

        if ckpt_path.exists():
            ckpt_path.unlink()
        print(
            json.dumps(
                {
                    "status": "completed",
                    "checkpoint_cleared": True,
                    "processed_llm_writes_last_wave": processed_wave,
                },
                indent=2,
            )
        )
        return


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill citation URLs on politician detail fields that lack them. "
            "Does not invent new facts — run scripts/run_politician_agent.py first."
        )
    )
    parser.add_argument("--id", help="Run only for a single Politician ID")
    parser.add_argument(
        "--type", choices=["MP", "MLA"], help="Run only for one election type"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit politicians processed (0 = no limit)",
    )
    parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"]
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--schedule",
        action="store_true",
        help=(
            "Run in a loop: save checkpoint on LLM quota, sleep, resume until queue done. "
            "Use RAJNITI_LLM_MAX_CALLS etc. via BaseAgent."
        ),
    )
    parser.add_argument(
        "--schedule-sleep-seconds",
        type=float,
        default=3600.0,
        help="With --schedule: seconds to sleep after quota before retrying (default: 3600)",
    )
    parser.add_argument(
        "--checkpoint-file",
        type=Path,
        default=_DEFAULT_CKPT,
        help="With --schedule: JSON checkpoint for resume",
    )
    parser.add_argument(
        "--reset-checkpoint",
        action="store_true",
        help="With --schedule: discard checkpoint before run",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.0,
        help="With --schedule: pause between politicians",
    )

    args = parser.parse_args()

    if args.schedule and args.id:
        parser.error("--schedule cannot be used with --id")

    setup_logging(args.log_level)

    agent = CitationAgent()

    if args.schedule:
        _run_schedule(agent, args)
        return

    result = agent.run(
        politician_id=args.id,
        election_type=args.type,
        force=args.force,
        limit=args.limit,
    )

    print(result)


if __name__ == "__main__":
    main()
