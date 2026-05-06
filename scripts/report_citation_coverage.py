#!/usr/bin/env python3
"""Report citation coverage for mp.json / mla.json detail fields."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.citation_audit_merge import politician_needs_citation_audit

_DATA = Path(__file__).resolve().parent.parent / "app" / "data"


def _load_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON summary",
    )
    args = parser.parse_args()

    mp_path = _DATA / "mp.json"
    mla_path = _DATA / "mla.json"
    rows = _load_list(mp_path) + _load_list(mla_path)
    total = len(rows)
    missing = [p for p in rows if politician_needs_citation_audit(p)]

    summary = {
        "total_politicians": total,
        "fully_cited": total - len(missing),
        "missing_citations": len(missing),
        "missing_ids": [p.get("id") for p in missing if p.get("id")],
    }

    if args.json:
        print(json.dumps(summary, indent=2))
        return 0

    print(f"Total politicians: {total}")
    print(f"Fully cited (details): {summary['fully_cited']}")
    print(f"Missing at least one citation: {summary['missing_citations']}")
    if missing and total <= 50:
        for p in missing:
            print(f"  - {p.get('name')} ({p.get('id')}) [{p.get('type')}]")
    elif missing:
        print(f"  (Use --json for full id list; {len(missing)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
