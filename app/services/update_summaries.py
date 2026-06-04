import json
from pathlib import Path

# This file lives in app/services, so go up two levels to the project root.
DATA_DIR = Path(__file__).resolve().parents[2] / "app" / "data"

def build_summary(politician: dict) -> str:
    name = politician.get("name", "This politician")
    state = politician.get("state") or "India"
    constituency = politician.get("constituency") or "this constituency"
    elections = (politician.get("political_background") or {}).get("elections") or []
    first = elections[0] if elections else {}
    party = first.get("party") or "the party"
    year = first.get("year") or "recent"

    return (
        f"{name} is an Indian politician from {state}, representing {constituency} "
        f"as a member of {party}. This entry reflects the {year} election result."
    )

def update_file(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    updated = 0

    for politician in data:
        pb = politician.setdefault("political_background", {})
        if not (pb.get("summary") or "").strip():
            pb["summary"] = build_summary(politician)
            pb.setdefault("summary_citation", None)
            updated += 1

    if updated:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return updated

def main():
    files = [DATA_DIR / "mp.json", DATA_DIR / "mla.json"]

    total = 0
    for file_path in files:
        if not file_path.exists():
            print(f"Skipping missing file: {file_path}")
            continue

        count = update_file(file_path)
        total += count
        print(f"{file_path.name}: updated {count} records")

    print(f"\nTotal summaries added: {total}")

if __name__ == "__main__":
    main()