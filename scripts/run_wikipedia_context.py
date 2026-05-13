#!/usr/bin/env python3
"""Live Wikipedia (and optional web-search) fetch — mirrors agent evidence gathering.

Runs real HTTP calls to English Wikipedia (+ DuckDuckGo when --full-context).
Does not invoke the LLM. For citation persistence use ``run_citation_agent.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict
from unittest.mock import MagicMock, patch

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))


def _load_politician(args: argparse.Namespace) -> Dict[str, Any]:
    if args.id:
        from app.services import PoliticianService

        svc = PoliticianService()
        p = svc.get_by_id(args.id)
        if not p:
            print(f"No politician found for id={args.id}", file=sys.stderr)
            sys.exit(1)
        return p

    if not args.name:
        print("Provide --name or --id.", file=sys.stderr)
        sys.exit(2)

    row: Dict[str, Any] = {
        "name": args.name.strip(),
        "state": (args.state or "").strip(),
        "constituency": (args.constituency or "").strip(),
    }
    if args.type:
        row["type"] = args.type.strip()
    return row


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Wikipedia politician_wikipedia_bundle and/or full BaseAgent-style "
            "context (structured Wikipedia + DuckDuckGo)."
        )
    )
    parser.add_argument("--name", help="Politician display name")
    parser.add_argument(
        "--id",
        metavar="POLITICIAN_ID",
        help="Load MP/MLA row from JSON by id (uses app/data/mp.json | mla.json)",
    )
    parser.add_argument("--state", default="", help="Used with --name only")
    parser.add_argument("--constituency", default="", help="Used with --name only")
    parser.add_argument("--type", choices=["MP", "MLA"], help="Used with --name only")
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="HTTP timeout seconds (default 15)",
    )
    parser.add_argument(
        "--full-context",
        action="store_true",
        help=(
            "Structured Wikipedia section + DuckDuckGo snippets (matches "
            "BaseAgent._gather_politician_context; LLM is mocked — no keys needed)."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit Wikipedia bundle as JSON instead of readable text (--full-context ignores this).",
    )
    args = parser.parse_args()

    if not args.id and not args.name:
        parser.error("One of --name or --id is required")

    pol = _load_politician(args)

    from app.tools.wikipedia_tool import WikipediaTool

    tool = WikipediaTool(timeout=args.timeout)

    bundle = tool.politician_wikipedia_bundle(
        str(pol.get("name") or ""),
        str(pol.get("state") or ""),
    )

    if args.full_context:
        from app.agents.base_agent import BaseAgent

        with patch("app.agents.base_agent.get_agent_llm", return_value=MagicMock()):
            agent = BaseAgent()
        blob = agent._gather_politician_context(pol)
        print(blob)
        if not blob.strip():
            return 1
        return 0

    # Default and --bundle-only: Wikipedia bundle (+ optional overlap hint)
    if args.json:
        print(json.dumps(bundle, indent=2, ensure_ascii=False))
        if bundle is None:
            return 1
        return 0

    if bundle is None:
        print("(no Wikipedia hit — try a different spelling or --full-context)")
        return 1

    print(f"Title: {bundle.get('title')}")
    print(f"Article URL: {bundle.get('article_url')}")
    print()
    print("Extract:")
    print(bundle.get("extract") or "(empty)")
    print()
    links = bundle.get("external_links") or []
    if links:
        print("Outbound links (filtered):")
        for i, u in enumerate(links, 1):
            print(f"  {i}. {u}")

    pb = pol.get("political_background") or {}
    summary = (pb.get("summary") or "").strip()
    ex = bundle.get("extract") or ""
    if summary and ex:
        from app.tools.wikipedia_tool import summary_matches_wikipedia_extract

        ok = summary_matches_wikipedia_extract(summary, ex)
        print()
        print(
            "summary_matches_wikipedia_extract (stored summary vs this extract): "
            f"{ok}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
