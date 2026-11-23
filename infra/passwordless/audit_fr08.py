"""Read-only, bounded lab audit. Outputs metadata/counts, never stored values.

Heuristics detect common key markers, not all possible private key encodings.
Run with apps/lab/.venv/Scripts/python.exe from the repository root.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
MARKER = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----|[\"'](?:private[_-]?key|privateKeyPkcs8|pkcs8)[\"']\s*:", re.I)


def signals(value):
    """Return counts only. JWK private components require a JWK-shaped object."""
    counts = {"private_named_fields": 0, "private_jwk_objects": 0, "text_markers": 0}
    def walk(item):
        if isinstance(item, dict):
            if item.get("kty") in ("RSA", "EC", "OKP") and "d" in item:
                counts["private_jwk_objects"] += 1
            for key, child in item.items():
                if re.fullmatch(r"private[_-]?key|privateKeyPkcs8|pkcs8", key, re.I):
                    counts["private_named_fields"] += 1
                walk(child)
        elif isinstance(item, list):
            for child in item: walk(child)
        elif isinstance(item, str):
            counts["text_markers"] += len(MARKER.findall(item))
    walk(value)
    return counts


def main():
    sys.path.insert(0, str(ROOT / "apps/lab"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    from django.db import connection, transaction
    from django.core import signing
    from django.contrib.sessions.backends.db import SessionStore

    report = {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Django public schema, up to 1000 sessions, named local logs and selected JSON/CSV evidence exports",
              "verdict": "PARTIAL_REVIEW_NOT_FULL_FR08_PASS"}
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute("SET LOCAL statement_timeout = '10s'")
                cursor.execute("SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name, ordinal_position")
                report["schema_columns"] = cursor.fetchall()
                cursor.execute("SELECT count(*) FROM django_session")
                report["session_rows_total"] = cursor.fetchone()[0]
                cursor.execute("SELECT session_data FROM django_session ORDER BY expire_date DESC LIMIT 1000")
                sessions = cursor.fetchall()
                summary = {"rows_scanned": len(sessions), "rows_decoded": 0, "decode_errors": 0, "decode_error_types": {}, "private_named_fields": 0,
                           "private_jwk_objects": 0, "text_markers": 0}
                for (encoded,) in sessions:
                    try:
                        decoded = signing.loads(encoded, salt=SessionStore().key_salt,
                                                serializer=SessionStore().serializer)
                        summary["rows_decoded"] += 1
                        for key, count in signals(decoded).items(): summary[key] += count
                    except Exception as exc:
                        summary["decode_errors"] += 1
                        name = type(exc).__name__
                        summary["decode_error_types"][name] = summary["decode_error_types"].get(name, 0) + 1
                report["sessions"] = summary
    except Exception as exc:
        report["database_error_type"] = type(exc).__name__

    paths = list((ROOT / "apps/lab/.runtime/logs").glob("*.log*"))
    paths += [ROOT / "tmp/lab-server.stdout.log", ROOT / "tmp/lab-server.stderr.log"]
    # Explicit scope: do not traverse secrets, volumes, VDT snapshots or keys.
    for folder in (ROOT / "docs/validation/passwordless-preflight",
                   ROOT / "docs/validation/callback-recovery-2026-11-23"):
        for suffix in ("*.json", "*.csv"):
            paths += list(folder.rglob(suffix))
    scanned = []
    for path in sorted(set(paths)):
        if not path.is_file(): continue
        row = {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size}
        if row["bytes"] > 8 * 1024 * 1024:
            row["status"] = "SKIPPED_SIZE_LIMIT"
        else:
            content = path.read_text(encoding="utf-8-sig", errors="replace")
            try:
                data = json.loads(content) if path.suffix == ".json" else content
                row.update(signals(data)); row["status"] = "SCANNED_HEURISTIC"
            except ValueError:
                row["status"] = "JSON_PARSE_FAILED"
        scanned.append(row)
    report["files"] = scanned
    source_paths = ["apps/lab/authn/models.py", "apps/lab/authn/services.py",
                    "apps/lab/authn/views.py", "apps/lab/authn/backchannel.py",
                    "apps/lab/authn/diagnostics.py", "apps/lab/config/oidc.py",
                    "apps/lab/config/settings.py", "infra/Caddyfile",
                    "infra/passwordless/inspect_keycloak.py", "infra/passwordless/audit_fr08.py"]
    report["source_sha256"] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in source_paths}
    report["not_inspected"] = ["Keycloak database", "Keycloak/Caddy container logs", "browser/Windows logs",
                               "arbitrary backups/exports", "all possible binary or encrypted key encodings"]
    out = ROOT / "docs/validation/fr08-2026-11-23"
    out.mkdir(parents=True, exist_ok=True)
    (out / "app-audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": report["verdict"], "schema_columns": len(report.get("schema_columns", [])),
                      "sessions": report.get("sessions"), "database_error_type": report.get("database_error_type"),
                      "files": scanned}, ensure_ascii=True))


if __name__ == "__main__":
    main()
