"""
Simple queue-based MLA fetcher.

Flow:
1. Check if state exists in states.json
2. Load existing MLA data for that state from mla.json
3. Fetch all constituency names from LLM
4. Build a queue of missing constituencies (not already in JSON)
5. Fetch MLA details one-by-one, persist each immediately
6. Skip any constituency already present in JSON
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.agents.base_agent import BaseAgent
from app.core.agent_logger import AgentLogger

logger = logging.getLogger(__name__)
alog = AgentLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 30.0  # seconds: 30, 60, 120

# States with 150+ seats need bucketed fetch to avoid output-limit issues.
LARGE_STATES = frozenset(
    {
        "Andhra Pradesh",
        "Assam",
        "Bihar",
        "Gujarat",
        "Karnataka",
        "Kerala",
        "Madhya Pradesh",
        "Maharashtra",
        "Odisha",
        "Punjab",
        "Rajasthan",
        "Tamil Nadu",
        "Telangana",
        "Uttar Pradesh",
        "West Bengal",
    }
)

LETTER_BUCKETS: List[tuple] = [
    ("A", "D"),
    ("E", "H"),
    ("I", "L"),
    ("M", "P"),
    ("Q", "S"),
    ("T", "Z"),
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class FetchResult:
    """Result returned after running the fetcher for a state."""

    ok: bool
    state: str
    constituencies_found: int = 0
    fetched: int = 0
    added: int = 0
    skipped: int = 0
    error: str = ""


@dataclass
class FetchQueue:
    """Simple event queue of constituencies to fetch."""

    state: str
    pending: deque = field(default_factory=deque)
    completed: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.pending) + len(self.completed) + len(self.failed)

    @property
    def remaining(self) -> int:
        return len(self.pending)

    def next(self) -> Optional[str]:
        if self.pending:
            return self.pending.popleft()
        return None

    def mark_done(self, constituency: str) -> None:
        self.completed.append(constituency)

    def mark_failed(self, constituency: str) -> None:
        self.failed.append(constituency)


# ---------------------------------------------------------------------------
# Pure Python helpers (no LLM)
# ---------------------------------------------------------------------------


def load_states(data_dir: Path) -> List[str]:
    """Load valid state names from states.json."""
    path = data_dir / "states.json"
    if not path.exists():
        logger.error("states.json not found at %s", path)
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def validate_state(state: str, valid_states: List[str]) -> Optional[str]:
    """Return canonical state name if it exists in states.json, else None."""
    norm = state.strip()
    for s in valid_states:
        if s.lower() == norm.lower():
            return s
    return None


def load_existing_mlas(mla_path: Path, state: str) -> List[Dict[str, Any]]:
    """Load existing MLA records for a specific state from mla.json."""
    if not mla_path.exists():
        return []
    try:
        all_records = json.loads(mla_path.read_text(encoding="utf-8"))
        return [r for r in all_records if r.get("state", "").lower() == state.lower()]
    except Exception as exc:
        logger.error("Failed to read mla.json: %s", exc)
        return []


def get_existing_constituencies(records: List[Dict[str, Any]]) -> set:
    """Extract set of constituency names (lowercased) from existing records."""
    return {
        r.get("constituency", "").strip().lower()
        for r in records
        if r.get("constituency")
    }


def state_has_data(mla_path: Path, state: str) -> bool:
    """Pure Python check: does this state already have ANY MLA data?"""
    records = load_existing_mlas(mla_path, state)
    return len(records) > 0


def make_id(name: str, state: str, constituency: str) -> str:
    """Deterministic UUID for an MLA record."""
    payload = f"{name.strip().lower()}|{state.strip().lower()}|{constituency.strip().lower()}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, payload))


def dedupe_key(name: str, constituency: str) -> str:
    return f"{name.strip().lower()}|{constituency.strip().lower()}"


# ---------------------------------------------------------------------------
# Persist helper
# ---------------------------------------------------------------------------


def persist_record(mla_path: Path, state: str, item: Dict[str, Any]) -> bool:
    """Persist a single MLA record to mla.json. Returns True if added."""
    name = (item.get("name") or "").strip()
    constituency = (item.get("constituency") or "").strip()
    if not name or not constituency:
        return False

    # Load current data
    existing: List[Dict[str, Any]] = []
    if mla_path.exists():
        try:
            existing = json.loads(mla_path.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    # Check for duplicate
    dkey = dedupe_key(name, constituency)
    for r in existing:
        if dedupe_key(r.get("name", ""), r.get("constituency", "")) == dkey:
            return False  # already exists

    # Build record
    record = {
        "id": make_id(name, state, constituency),
        "name": name,
        "photo": item.get("photo"),
        "state": state,
        "constituency": constituency,
        "party": item.get("party"),
        "type": "MLA",
        "education": None,
        "family_background": None,
        "criminal_records": None,
        "social_media": None,
        "contact": None,
        "political_background": {"elections": [], "summary": None},
    }

    existing.append(record)

    # Atomic write
    tmp = mla_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(mla_path)
    return True


# ---------------------------------------------------------------------------
# LLM fetch functions (with retry)
# ---------------------------------------------------------------------------


def _is_retryable(exc: Exception) -> bool:
    """Check if error warrants a retry (timeout/rate-limit)."""
    msg = str(exc).lower()
    class_name = type(exc).__name__.lower()

    indicators = (
        "timeout", "deadline", "504", "503", "429",
        "rate limit", "resource exhausted", "too many requests",
        "overloaded", "all candidates skipped or failed", "cooldown",
    )

    if any(kw in class_name for kw in ("timeout", "deadline")):
        return True
    if any(kw in msg for kw in indicators):
        return True

    status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if isinstance(status_code, int) and status_code in (429, 500, 502, 503, 504):
        return True
    return False


def _retry_llm_call(agent: BaseAgent, prompt: str, label: str) -> Optional[str]:
    """Run an LLM call with retry logic. Returns raw response or None."""
    for attempt in range(1, MAX_RETRIES + 1):
        t0 = time.perf_counter()
        try:
            raw = agent._run_llm(prompt)
            elapsed = time.perf_counter() - t0
            alog.llm_call_success(
                call_id=agent._llm_call_count,
                provider=getattr(agent.llm, "active_provider", "unknown"),
                model=getattr(agent.llm, "model_name", "unknown"),
                response_chars=len(raw),
                elapsed_s=elapsed,
            )
            return raw
        except Exception as exc:
            elapsed = time.perf_counter() - t0
            is_retry = _is_retryable(exc) and attempt < MAX_RETRIES

            alog.llm_call_failed(
                call_id=agent._llm_call_count + 1,
                provider=getattr(agent.llm, "active_provider", "unknown"),
                model=getattr(agent.llm, "model_name", "unknown"),
                elapsed_s=elapsed,
                error=str(exc),
                error_class=type(exc).__name__,
                will_retry=is_retry,
                retry_num=attempt,
                max_retries=MAX_RETRIES,
            )

            if not is_retry:
                logger.error("[%s] Failed permanently: %s", label, str(exc)[:200])
                return None

            wait = RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
            alog.retry(label, attempt=attempt, max_attempts=MAX_RETRIES, wait_s=wait, error=str(exc)[:100])
            time.sleep(wait)

            # Clear FreeTierLLM cooldown so retry reaches the API
            if hasattr(agent.llm, "clear_cooldowns"):
                agent.llm.clear_cooldowns()

    return None


def fetch_all_constituencies(agent: BaseAgent, state: str) -> List[str]:
    """Fetch all constituency names for a state."""
    alog.step("fetch_constituencies", f"Fetching for {state}")

    is_large = state in LARGE_STATES

    if not is_large:
        result = _fetch_constituencies_single(agent, state)
        if result:
            return result
        # Fallback to bucketed
        logger.info("[fetch_constituencies] Single-shot empty, falling back to buckets")

    return _fetch_constituencies_bucketed(agent, state)


def _fetch_constituencies_single(agent: BaseAgent, state: str) -> List[str]:
    """Single-shot fetch for small states."""
    prompt = (
        f"Return ONLY a valid JSON array of all current assembly constituency names "
        f"for the Indian state: {state}.\n"
        f'Example format: ["Dispur", "Jalukbari", ...]\n'
    )

    alog.llm_call_start(
        call_id=agent._llm_call_count + 1,
        provider=getattr(agent.llm, "active_provider", "unknown"),
        model=getattr(agent.llm, "model_name", "unknown"),
        prompt_chars=len(prompt),
    )

    raw = _retry_llm_call(agent, prompt, f"constituencies_{state}")
    if not raw:
        return []

    parsed = agent._parse_json_value(raw)
    if parsed is None:
        return []

    items = agent._coerce_to_list(parsed) or []
    result = [c.strip() for c in items if isinstance(c, str) and c.strip()]
    logger.info("[fetch_constituencies] %s → %d names (single-shot)", state, len(result))
    return result


def _fetch_constituencies_bucketed(agent: BaseAgent, state: str) -> List[str]:
    """Bucketed fetch for large states."""
    logger.info("[fetch_constituencies] Using letter buckets for %s", state)
    seen: set = set()
    merged: List[str] = []

    for i, (lo, hi) in enumerate(LETTER_BUCKETS):
        if i > 0:
            time.sleep(0.5)

        bucket_key = f"{lo}-{hi}"
        prompt = (
            f'Return ONLY a valid JSON array of assembly constituency names in "{state}" '
            f"whose names start with letters {lo!r} through {hi!r} inclusive. "
            f"Include every constituency in this letter range; omit names outside it. "
            f'Format: ["Name1", "Name2", ...]\n'
        )

        alog.llm_call_start(
            call_id=agent._llm_call_count + 1,
            provider=getattr(agent.llm, "active_provider", "unknown"),
            model=getattr(agent.llm, "model_name", "unknown"),
            prompt_chars=len(prompt),
        )

        raw = _retry_llm_call(agent, prompt, f"bucket_{bucket_key}_{state}")
        if not raw:
            logger.warning("[bucket_%s] No response, skipping", bucket_key)
            continue

        parsed = agent._parse_json_value(raw)
        if parsed is None:
            continue

        items = agent._coerce_to_list(parsed) or []
        for c in items:
            if isinstance(c, str) and c.strip():
                key = c.strip().lower()
                if key not in seen:
                    seen.add(key)
                    merged.append(c.strip())

        logger.info("[bucket_%s] → %d new, total=%d", bucket_key, len(items), len(merged))

    logger.info("[fetch_constituencies] %s → %d total (bucketed)", state, len(merged))
    return merged


def fetch_mla_for_constituency(
    agent: BaseAgent, state: str, constituency: str
) -> Optional[Dict[str, Any]]:
    """Fetch MLA details for a single constituency. Returns record or None."""
    prompt = (
        f"For the constituency \"{constituency}\" in {state}, return the current MLA.\n"
        f"Return ONLY a valid JSON object with keys: \"name\", \"constituency\", \"party\".\n"
        f"Example: {{\"name\": \"Rahul Sharma\", \"constituency\": \"{constituency}\", \"party\": \"BJP\"}}\n"
    )

    alog.llm_call_start(
        call_id=agent._llm_call_count + 1,
        provider=getattr(agent.llm, "active_provider", "unknown"),
        model=getattr(agent.llm, "model_name", "unknown"),
        prompt_chars=len(prompt),
    )

    raw = _retry_llm_call(agent, prompt, f"mla_{constituency}")
    if not raw:
        return None

    parsed = agent._parse_json_value(raw)
    if parsed is None:
        return None

    # Handle if response is a list with one item
    if isinstance(parsed, list):
        parsed = parsed[0] if parsed else None
    if not isinstance(parsed, dict):
        return None

    name = (parsed.get("name") or "").strip()
    if not name:
        return None

    return {
        "name": name,
        "constituency": (parsed.get("constituency") or constituency).strip(),
        "party": (parsed.get("party") or "").strip(),
    }


def fetch_mlas_batch(
    agent: BaseAgent, state: str, constituencies: List[str]
) -> List[Dict[str, Any]]:
    """Fetch MLA details for a small batch of constituencies (max 5 at a time)."""
    constituency_json = json.dumps(constituencies, ensure_ascii=False)
    prompt = (
        f"For each constituency listed below in {state}, return the current MLA.\n"
        f"Return ONLY a valid JSON array. Each item must have: "
        f'"name", "constituency", "party".\n'
        f"Constituencies: {constituency_json}\n"
    )

    alog.llm_call_start(
        call_id=agent._llm_call_count + 1,
        provider=getattr(agent.llm, "active_provider", "unknown"),
        model=getattr(agent.llm, "model_name", "unknown"),
        prompt_chars=len(prompt),
    )

    raw = _retry_llm_call(agent, prompt, f"mla_batch_{len(constituencies)}")
    if not raw:
        return []

    parsed = agent._parse_json_value(raw)
    if parsed is None:
        return []

    items = agent._coerce_to_list(parsed) or []
    return [
        d for d in items
        if isinstance(d, dict) and d.get("name") and d.get("constituency")
    ]


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def run_fetcher(
    agent: BaseAgent,
    state: str,
    data_dir: Path,
    force: bool = False,
    dry_run: bool = False,
    batch_size: int = 5,
) -> FetchResult:
    """
    Main entry point. Runs the full fetch pipeline for one state.

    1. Validate state exists in states.json
    2. Check existing data in mla.json
    3. Fetch constituency list from LLM
    4. Build queue of missing constituencies
    5. Fetch MLA for each missing constituency, persist immediately
    """
    mla_path = data_dir / "mla.json"
    result = FetchResult(ok=False, state=state)

    # --- Step 1: Validate state ---
    valid_states = load_states(data_dir)
    canonical = validate_state(state, valid_states)
    if not canonical:
        result.error = f"State '{state}' not found in states.json"
        logger.error("[run_fetcher] %s", result.error)
        return result

    result.state = canonical
    alog.step("run_fetcher", f"Starting for {canonical}", details={"force": force, "dry_run": dry_run})

    # --- Step 2: Check existing data ---
    existing_records = load_existing_mlas(mla_path, canonical)
    existing_constituencies = get_existing_constituencies(existing_records)

    has_data = len(existing_records) > 0
    alog.step(
        "check_existing",
        f"{canonical}: {len(existing_records)} records, {len(existing_constituencies)} constituencies",
    )

    if dry_run:
        logger.info("[dry-run] %s: %d existing records", canonical, len(existing_records))
        result.ok = True
        result.constituencies_found = len(existing_constituencies)
        return result

    # --- Step 3: Fetch all constituencies ---
    all_constituencies = fetch_all_constituencies(agent, canonical)
    if not all_constituencies:
        result.error = "Failed to fetch constituency list"
        logger.error("[run_fetcher] %s", result.error)
        return result

    result.constituencies_found = len(all_constituencies)
    alog.step(
        "constituencies_fetched",
        f"{canonical}: {len(all_constituencies)} constituencies from LLM",
    )

    # --- Step 4: Build queue of missing constituencies ---
    if force:
        missing = all_constituencies
    else:
        missing = [
            c for c in all_constituencies
            if c.strip().lower() not in existing_constituencies
        ]

    if not missing:
        alog.step("queue", f"{canonical}: All constituencies already have MLA data — nothing to fetch")
        result.ok = True
        return result

    queue = FetchQueue(state=canonical, pending=deque(missing))
    alog.step(
        "queue",
        f"{canonical}: {queue.remaining} constituencies to fetch",
        details={"total_known": len(all_constituencies), "already_have": len(existing_constituencies)},
    )

    # --- Step 5: Fetch MLAs and persist each immediately ---
    alog.step("fetch_mlas", f"Processing queue of {queue.remaining} constituencies (batch_size={batch_size})")

    while queue.remaining > 0:
        # Grab a batch from the queue
        batch: List[str] = []
        for _ in range(min(batch_size, queue.remaining)):
            item = queue.next()
            if item:
                batch.append(item)

        if not batch:
            break

        # Check again if these constituencies are now in the JSON
        # (in case a previous batch already covered them via LLM returning extra data)
        batch_to_fetch = []
        for c in batch:
            if c.strip().lower() in existing_constituencies and not force:
                queue.mark_done(c)
                result.skipped += 1
            else:
                batch_to_fetch.append(c)

        if not batch_to_fetch:
            continue

        # Fetch MLA details
        if len(batch_to_fetch) == 1:
            mla = fetch_mla_for_constituency(agent, canonical, batch_to_fetch[0])
            records = [mla] if mla else []
        else:
            records = fetch_mlas_batch(agent, canonical, batch_to_fetch)

        # Persist each record immediately
        for record in records:
            added = persist_record(mla_path, canonical, record)
            if added:
                result.added += 1
                # Update the existing set so we don't re-fetch
                existing_constituencies.add(record.get("constituency", "").strip().lower())
                logger.info(
                    "[persisted] %s | %s | %s",
                    record.get("name"), record.get("constituency"), record.get("party"),
                )
            else:
                result.skipped += 1

        # Mark batch items as done/failed
        fetched_constituencies = {r.get("constituency", "").strip().lower() for r in records}
        for c in batch_to_fetch:
            if c.strip().lower() in fetched_constituencies:
                queue.mark_done(c)
            else:
                queue.mark_failed(c)

        result.fetched += len(records)

        # Rate limit between batches
        if queue.remaining > 0:
            time.sleep(0.5)

    # --- Done ---
    result.ok = True
    alog.step(
        "run_fetcher",
        f"DONE for {canonical} | added={result.added} fetched={result.fetched} skipped={result.skipped}",
    )

    if queue.failed:
        logger.warning(
            "[run_fetcher] %d constituencies failed to fetch: %s",
            len(queue.failed),
            queue.failed[:10],
        )

    return result
