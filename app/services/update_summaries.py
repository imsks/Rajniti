import json
from pathlib import Path

# This file lives in app/services, so go up two levels to the project root.
DATA_DIR = Path(__file__).resolve().parents[2] / "app" / "data"


def _clean_text(value: str | None) -> str:
    return " ".join((value or "").split()).strip()


def _latest_election(politician: dict) -> dict:
    elections = (politician.get("political_background") or {}).get("elections") or []
    return max(elections, key=lambda item: (item.get("year") or 0, item.get("status") == "WON"), default={})


def _education_line(politician: dict) -> str:
    education = politician.get("education") or []
    if not education:
        return ""

    first = education[0] or {}
    qualification = _clean_text(first.get("qualification"))
    institution = _clean_text(first.get("institution"))

    if qualification and institution:
        return f" {qualification.title()} from {institution}."
    if qualification:
        return f" {qualification.title()}."
    if institution:
        return f" Educated at {institution}."
    return ""


def build_summary(politician: dict) -> str:
    name = _clean_text(politician.get("name")) or "This politician"
    state = _clean_text(politician.get("state")) or "India"
    constituency = _clean_text(politician.get("constituency")) or "this constituency"
    office = _clean_text(politician.get("type")) or "politician"
    elections = sorted(
        (politician.get("political_background") or {}).get("elections") or [],
        key=lambda item: (item.get("year") or 0, item.get("status") == "WON"),
        reverse=True,
    )
    latest = elections[0] if elections else {}

    current_party = _clean_text(latest.get("party")) or "the party"
    current_year = latest.get("year") or "recently"
    current_status = _clean_text(latest.get("status")) or "contested"

    previous = elections[1] if len(elections) > 1 else {}
    previous_party = _clean_text(previous.get("party"))
    previous_year = previous.get("year")
    previous_seat = _clean_text(previous.get("constituency")) or constituency

    if previous_party and previous_year:
        history_line = (
            f" Earlier, {name} was associated with {previous_party} in {previous_year}, "
            f"and the record shows a move toward the {current_party} banner for {constituency}."
        )
    else:
        history_line = f" The latest record places {name} in {state} with the {current_party} ticket for {constituency}."

    education_line = _education_line(politician)

    if office.upper() == "MP":
        office_text = f"Member of Parliament from {constituency}"
    elif office.upper() == "MLA":
        office_text = f"Member of the Legislative Assembly from {constituency}"
    else:
        office_text = f"politician representing {constituency}"

    return (
        f"{name} is a {state} leader and {office_text}. "
        f"The latest available result shows {name} winning the {current_year} election from {constituency} "
        f"as a {current_party} candidate ({current_status}).{history_line}{education_line}"
    ).replace("  ", " ").strip()

def update_file(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    updated = 0

    for politician in data:
        pb = politician.setdefault("political_background", {})
        new_summary = build_summary(politician)
        old_summary = (pb.get("summary") or "").strip()

        if old_summary != new_summary:
            pb["summary"] = new_summary
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