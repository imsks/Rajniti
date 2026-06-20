"""CLI: fetch politician data from external sources."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core import setup_logging
from app.services import PoliticianService
from app.sources.orchestrator import SourceOrchestrator

logger = logging.getLogger(__name__)

_DEFAULT_CKPT = (
    Path(__file__).resolve().parents[1] / ".cache" / "source_scraper_checkpoint.json"
)


def _load_checkpoint(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"last_id": None, "last_index": -1}
    try:
        with path.open(encoding="utf-8") as f:
            return {**{"last_id": None, "last_index": -1}, **json.load(f)}
    except Exception:
        return {"last_id": None, "last_index": -1}


def _save_checkpoint(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def _select_politicians(
    service: PoliticianService,
    *,
    politician_type: Optional[str],
    politician_id: Optional[str],
    limit: Optional[int],
) -> List[Dict[str, Any]]:
    if politician_id:
        p = service.get_by_id(politician_id)
        if not p:
            raise SystemExit(f"Politician not found: {politician_id}")
        return [p]
    if politician_type in ("MP", "MLA"):
        politicians = service.get_all(politician_type)
    else:
        politicians = service.get_all_politicians()
    if limit and limit > 0:
        politicians = politicians[:limit]
    return politicians


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scrape politician profiles from external sources"
    )
    parser.add_argument("--type", choices=["MP", "MLA"], default=None)
    parser.add_argument("--id", default=None, help="Single politician UUID")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="Re-fetch even if source_sync exists")
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help="Source name (repeatable), e.g. myneta",
    )
    parser.add_argument("--checkpoint-file", type=Path, default=_DEFAULT_CKPT)
    parser.add_argument("--reset-checkpoint", action="store_true")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    args = parser.parse_args(argv)

    setup_logging(args.log_level)
    service = PoliticianService()
    orchestrator = SourceOrchestrator(politician_service=service)

    politicians = _select_politicians(
        service,
        politician_type=args.type,
        politician_id=args.id,
        limit=None if args.id else args.limit,
    )

    if args.reset_checkpoint and args.checkpoint_file.exists():
        args.checkpoint_file.unlink()

    cp = _load_checkpoint(args.checkpoint_file)
    start_idx = int(cp.get("last_index", -1)) + 1
    last_id = cp.get("last_id")
    if last_id and not args.id:
        id_list = [str(p.get("id")) for p in politicians if p.get("id")]
        if last_id in id_list:
            start_idx = id_list.index(last_id) + 1

    source_names = args.source or None
    results: List[Dict[str, Any]] = []

    for idx in range(start_idx, len(politicians)):
        p = politicians[idx]
        pid = p.get("id")
        logger.info(
            "Source scrape [%d/%d] id=%s name=%s",
            idx + 1,
            len(politicians),
            pid,
            p.get("name"),
        )
        try:
            result = orchestrator.sync_politician(
                p,
                source_names=source_names,
                force=args.force,
            )
            results.append(result)
            if pid:
                _save_checkpoint(
                    args.checkpoint_file,
                    {"last_id": str(pid), "last_index": idx},
                )
        except Exception as exc:
            logger.exception("Source scrape failed for %s: %s", pid, exc)
            results.append({"id": pid, "ok": False, "errors": [str(exc)]})

    ok = sum(1 for r in results if r.get("ok"))
    logger.info("Done: %d/%d succeeded", ok, len(results))
    print(json.dumps({"processed": len(results), "ok": ok, "results": results}, indent=2))
    return 0 if ok == len(results) or not results else 1


if __name__ == "__main__":
    raise SystemExit(main())
