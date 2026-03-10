"""
Fetch GitHub contributors for imsks/rajniti and write a deterministic JSON
file consumed by the Next.js frontend.

Usage:
    python scripts/generate_contributors.py              # default output
    python scripts/generate_contributors.py --out /tmp/c.json

Set GITHUB_TOKEN in the environment for higher rate limits.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

REPO = "imsks/rajniti"
API_URL = f"https://api.github.com/repos/{REPO}/contributors"
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "frontend" / "data" / "contributors.json"


def fetch_contributors(token: str | None = None) -> list[dict]:
    """Paginate through the GitHub contributors endpoint."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    contributors: list[dict] = []
    page = 1

    while True:
        url = f"{API_URL}?per_page=100&page={page}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            print(f"GitHub API error: {exc.code} {exc.reason}", file=sys.stderr)
            sys.exit(1)

        if not data:
            break

        for entry in data:
            if entry.get("type") != "User":
                continue
            contributors.append({
                "login": entry["login"],
                "avatar_url": entry["avatar_url"],
                "html_url": entry["html_url"],
                "contributions": entry["contributions"],
            })

        page += 1

    contributors.sort(key=lambda c: (-c["contributions"], c["login"]))
    return contributors


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate contributors.json")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output path")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    contributors = fetch_contributors(token)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(contributors, indent=2) + "\n")
    print(f"Wrote {len(contributors)} contributors to {args.out}")


if __name__ == "__main__":
    main()
