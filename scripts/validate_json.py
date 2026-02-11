#!/usr/bin/env python3
"""
Validate politician JSON files against the app.schemas.politician.Politician model.

Usage:
  python scripts/validate_json.py                     # validates app/data/ by default
  python scripts/validate_json.py app/data            # validate all .json files under app/data
  python scripts/validate_json.py app/data/mp.json app/data/mla.json

Exits with code 0 on success, 1 on validation errors.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List, Tuple

from pydantic import ValidationError

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.politician import Politician


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_file(path: Path) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    try:
        data = load_json(path)
    except Exception as exc:  # pragma: no cover - best-effort for CLI
        errors.append(f"Failed to load JSON: {exc}")
        return False, errors

    if isinstance(data, dict):
        # support object-of-id -> object format by converting to list
        items = list(data.values())
    elif isinstance(data, list):
        items = data
    else:
        errors.append(f"Top-level JSON must be an array or object, got {type(data).__name__}")
        return False, errors

    seen_ids = set()
    for idx, item in enumerate(items):
        location = f"{path}:{idx}"
        try:
            p = Politician.parse_obj(item)
        except ValidationError as ve:
            errors.append(f"{location} - validation error:\n{ve}")
            continue

        # check unique id
        if p.id in seen_ids:
            errors.append(f"{location} - duplicate id '{p.id}'")
        else:
            seen_ids.add(p.id)

        # Basic file-level sanity: ensure file name matches politician type when obvious
        name_lower = path.name.lower()
        if "mp" in name_lower and p.type != "MP":
            errors.append(f"{location} - expected type 'MP' (file '{path.name}') but got '{p.type}'")
        if "mla" in name_lower and p.type != "MLA":
            errors.append(f"{location} - expected type 'MLA' (file '{path.name}') but got '{p.type}'")

    ok = len(errors) == 0
    return ok, errors


def collect_json_files(path: Path) -> List[Path]:
    if path.is_dir():
        return sorted([p for p in path.rglob("*.json") if p.is_file()])
    if path.is_file():
        return [path]
    return []


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate politician JSON files or directories containing JSON files.")
    parser.add_argument(
        "paths",
        nargs="*",
        default=["app/data"],
        help="Files or directories to validate (if directory, all .json files are checked). Defaults to 'app/data' when omitted.",
    )
    args = parser.parse_args(argv)

    any_errors = False
    files_to_check: List[Path] = []
    for p in args.paths:
        path = Path(p)
        found = collect_json_files(path)
        if not found:
            print(f"Warning: no JSON files found at {path}", file=sys.stderr)
            continue
        files_to_check.extend(found)

    # Deduplicate and sort
    files_to_check = sorted(dict.fromkeys(files_to_check))
    if not files_to_check:
        print("No JSON files to validate.", file=sys.stderr)
        return 2

    for path in files_to_check:
        print(f"Validating {path} ...")
        ok, errors = validate_file(path)
        if ok:
            print(f"  OK: {path} (no validation errors)")
        else:
            any_errors = True
            print(f"  ERRORS in {path}:")
            for e in errors:
                print("   -", e)

    if any_errors:
        print("\nValidation failed.", file=sys.stderr)
        return 1
    print("\nAll files validated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

