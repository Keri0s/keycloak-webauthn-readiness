"""CSV and JSONL persistence for the WebAuthn evidence ledger."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Iterable, Mapping

from apps.ledger.schema import COLUMNS


def _sanitize_row(raw: Mapping[str, object]) -> dict[str, str]:
    """Keep strictly allowlisted COLUMNS and coerce missing values to empty strings."""
    cleaned: dict[str, str] = {}
    for col in COLUMNS:
        val = raw.get(col)
        cleaned[col] = val if isinstance(val, str) else ("" if val is None else str(val))
    return cleaned


def load_rows(path: Path) -> list[dict[str, str]]:
    """Load ledger rows from CSV, dropping any non-allowlisted columns."""
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return [_sanitize_row(row) for row in reader if row.get("evidence_id")]


def _sort_key(row: Mapping[str, str]) -> tuple[str, str]:
    raw_ts = row.get("occurred_at_utc", "")
    try:
        normalized = datetime.fromisoformat(raw_ts).astimezone(timezone.utc).isoformat()
    except ValueError:
        normalized = raw_ts
    return (normalized, row.get("evidence_id", ""))


def merge(
    existing: Iterable[Mapping[str, str]],
    new: Iterable[Mapping[str, str]],
) -> tuple[list[dict[str, str]], int, int]:
    """Deduplicate by evidence_id (preserving existing entries) and sort chronologically."""
    by_id: dict[str, dict[str, str]] = {}
    for raw in existing:
        row = _sanitize_row(raw)
        ev_id = row["evidence_id"]
        if ev_id and ev_id not in by_id:
            by_id[ev_id] = row

    added = 0
    duplicates = 0
    for raw in new:
        row = _sanitize_row(raw)
        ev_id = row["evidence_id"]
        if not ev_id:
            continue
        if ev_id in by_id:
            duplicates += 1
        else:
            by_id[ev_id] = row
            added += 1

    ordered = sorted(by_id.values(), key=_sort_key)
    return ordered, added, duplicates


def save_rows(path: Path, rows: Iterable[Mapping[str, str]]) -> None:
    """Atomically write allowlisted ledger rows to UTF-8 CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=".tmp_ledger_",
            suffix=".csv",
            delete=False,
        ) as stream:
            tmp_path = Path(stream.name)
            writer = csv.DictWriter(stream, fieldnames=COLUMNS, extrasaction="ignore")
            writer.writeheader()
            for raw in rows:
                writer.writerow(_sanitize_row(raw))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def compute_ledger_hashes(root: Path) -> dict[str, str]:
    """Return SHA-256 digests of the ledger source modules for audit metadata."""
    module_paths = (
        "apps/ledger/schema.py",
        "apps/ledger/mapping.py",
        "apps/ledger/store.py",
        "apps/ledger/keycloak.py",
        "apps/ledger/cli.py",
    )
    hashes: dict[str, str] = {}
    for rel in module_paths:
        target = root / rel
        if target.is_file():
            hashes[rel] = hashlib.sha256(target.read_bytes()).hexdigest()
    return hashes


def append_pull_log(path: Path, record: Mapping[str, object]) -> None:
    """Append one pull execution metadata record as JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(line)
        stream.flush()
        os.fsync(stream.fileno())
