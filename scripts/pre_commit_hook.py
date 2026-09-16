#!/usr/bin/env python3
"""
Pre-commit hook: auto-stamps lastUpdated on changed politician records in
mp.json and mla.json. Install as `.git/hooks/pre-commit`.

Flow:
  1. Checks which politician records changed (by hash comparison).
  2. Stamps `lastUpdated` on changed/new records.
  3. Re-stages the modified JSON files so the commit includes the timestamps.
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(result.stdout.strip())


def _staged_files() -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=True,
    )
    return set(result.stdout.splitlines())


def _compute_hash(record: dict) -> str:
    data = {k: v for k, v in record.items() if k not in {"lastUpdated", "slug", "performance"}}
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def _process_file(
    path: Path,
    old_hashes: dict,
    new_hashes: dict,
    now: str,
) -> bool:
    """Stamp lastUpdated on changed records. Returns True if the file was modified."""
    if not path.exists():
        return False

    with open(path, encoding="utf-8") as f:
        records = json.load(f)

    modified = False
    for rec in records:
        pid = str(rec.get("id", ""))
        if not pid:
            continue

        current_hash = _compute_hash(rec)
        new_hashes[pid] = current_hash

        if old_hashes.get(pid) != current_hash:
            rec["lastUpdated"] = now
            modified = True

    if modified:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return modified


def main() -> None:
    root = _repo_root()
    data_dir = root / "app" / "data"
    hash_file = data_dir / ".politician_hashes.json"

    staged = _staged_files()
    target_files = {"app/data/mp.json", "app/data/mla.json"}
    if not staged & target_files:
        sys.exit(0)

    old_hashes: dict = {}
    if hash_file.exists():
        try:
            old_hashes = json.loads(hash_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
          f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"
    new_hashes = dict(old_hashes)
    to_restage: list[str] = []

    for name in ("mp.json", "mla.json"):
        path = data_dir / name
        if _process_file(path, old_hashes, new_hashes, now):
            to_restage.append(str(path))
            print(f"[pre-commit] stamped lastUpdated in {name}")

    hash_file.write_text(
        json.dumps(new_hashes, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    to_restage.append(str(hash_file))

    subprocess.run(["git", "add"] + to_restage, check=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
