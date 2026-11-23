"""Inventory explicit project artifact roots; persist paths/counts only."""
import csv
import hashlib
import io
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from audit_fr08 import ROOT, signals

ROOTS = ("apps", "docs", "evidence", "infra", "tmp", "tests", "DU_LIEU_MAU/N15_San_sang_WebAuthn")
SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__", ".runtime", ".pytest_cache"}
TEXT = {".json", ".csv", ".jsonl", ".ndjson"}
BACKUP = {".dump", ".bak", ".backup", ".zip", ".gz", ".tar", ".7z", ".sqlite", ".sqlite3", ".db"}


def main():
    report = {"at_utc": datetime.now(timezone.utc).isoformat(), "roots": ROOTS,
              "excluded": ["references", "review", "other sample projects", "runtime volumes",
                           "dependencies", "symlinks/junctions", "outside project", "unrecognized file formats"],
              "files": [], "excluded_paths": [], "walk_errors": []}
    for folder in ROOTS:
        for current, dirs, files in os.walk(ROOT / folder, followlinks=False,
                onerror=lambda exc: report["walk_errors"].append(type(exc).__name__)):
            kept = []
            for d in dirs:
                p = Path(current) / d
                if d in SKIP or p.is_symlink() or p.is_junction():
                    report["excluded_paths"].append(p.relative_to(ROOT).as_posix())
                else:
                    kept.append(d)
            dirs[:] = kept
            for name in sorted(files):
                p = Path(current) / name
                if p.is_symlink() or p.suffix.lower() not in TEXT | BACKUP | {".sql"}:
                    continue
                rel = p.relative_to(ROOT).as_posix()
                if p.name.startswith("export-inventory-"):
                    continue  # Avoid counting previous inventories as target exports.
                row = {"path": rel, "bytes": p.stat().st_size}
                if p.suffix.lower() in BACKUP:
                    row["status"] = "BACKUP_OR_BINARY_REQUIRES_REVIEW"
                elif p.suffix.lower() == ".sql":
                    row["status"] = "SQL_SOURCE_NOT_EXPORT" if rel in (
                        "infra/passwordless/fr08-keycloak.sql", "infra/passwordless/fr08-events-long.sql"
                    ) else "SQL_REQUIRES_CLASSIFICATION"
                elif row["bytes"] > 8 * 1024 * 1024:
                    row["status"] = "SKIPPED_SIZE_LIMIT"
                else:
                    raw = p.read_bytes()
                    row["sha256"] = hashlib.sha256(raw).hexdigest()
                    try:
                        body = raw.decode("utf-8-sig")
                        if p.suffix.lower() == ".json":
                            value = json.loads(body)
                        elif p.suffix.lower() in {".jsonl", ".ndjson"}:
                            value = [json.loads(line) for line in body.splitlines() if line.strip()]
                        else:
                            value = list(csv.reader(io.StringIO(body)))
                        row["signals"] = signals(value)
                        row["status"] = "SCANNED_HEURISTIC"
                    except (ValueError, csv.Error, RecursionError) as exc:
                        row["status"] = "PARSE_FAILED"
                        row["error_type"] = type(exc).__name__
                report["files"].append(row)
    report["counts"] = dict(Counter(r["status"] for r in report["files"]))
    report["flagged_paths"] = [r["path"] for r in report["files"] if any(r.get("signals", {}).values())]
    report["verdict"] = "BOUNDED_INVENTORY_NOT_WHOLE_MACHINE_AUDIT"
    path = ROOT / "docs/validation/fr08-2026-11-23/export-inventory-2026-11-23.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("counts", "flagged_paths", "walk_errors", "verdict")}, indent=2))


if __name__ == "__main__":
    main()
