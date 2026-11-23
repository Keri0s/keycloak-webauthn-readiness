"""Read-only session diagnostics; emit only metadata, never session values/keys."""
import json
import os
import sys
import base64
import zlib
from collections import Counter
from datetime import datetime, timezone
from audit_fr08 import ROOT, signals


def inspect_untrusted_payload(encoded):
    """Decode bounded JSON for forensic review only; NEVER authenticate it."""
    if len(encoded) > 131072:
        raise ValueError("size limit")
    part = encoded.rsplit(":", 2)[0]
    compressed = part.startswith(".")
    if compressed:
        part = part[1:]
    raw = base64.b64decode(part + "=" * (-len(part) % 4), altchars=b"-_", validate=True)
    if compressed:
        decoder = zlib.decompressobj()
        raw = decoder.decompress(raw, 65537)
        if len(raw) > 65536 or not decoder.eof or decoder.unused_data:
            raise ValueError("compressed size or format limit")
    if len(raw) > 65536:
        raise ValueError("size limit")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("not a session object")
    return {"status": "JSON_DECODED_SIGNATURE_STILL_INVALID", "compressed": compressed,
            "field_count": len(value),
            "has_auth_fields": any(k in value for k in ("_auth_user_id", "_auth_user_backend", "_auth_user_hash")),
            "has_oidc_state_fields": any(k.startswith("_state_") for k in value),
            "signals": signals(value)}


def main():
    sys.path.insert(0, str(ROOT / "apps/lab"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    from django.core import signing
    from django.db import connection, transaction
    from django.contrib.sessions.backends.db import SessionStore

    now = datetime.now(timezone.utc)
    report = {"at_utc": now.isoformat(), "read_only": True, "invalid_rows": []}
    counts = Counter()
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            cursor.execute("SET LOCAL statement_timeout = '10s'")
            cursor.execute("SELECT count(*) FROM django_session")
            report["total_rows"] = cursor.fetchone()[0]
            cursor.execute("""SELECT s.session_data, s.expire_date,
                b.id IS NOT NULL, b.created_at, b.expires_at, b.revoked_at IS NOT NULL,
                g.revoked_at IS NOT NULL
                FROM django_session s
                LEFT JOIN authn_sessionbinding b ON b.session_key=s.session_key
                LEFT JOIN authn_oidcsessiongroup g ON g.id=b.group_id
                ORDER BY s.expire_date DESC LIMIT 1000""")
            rows = cursor.fetchall()
            report["scanned_rows"] = len(rows)
            for encoded, expiry, bound, created, binding_expiry, revoked, group_revoked in rows:
                try:
                    signing.loads(encoded, salt=SessionStore().key_salt,
                                  serializer=SessionStore().serializer)
                    counts["verified_rows"] += 1
                except Exception as exc:
                    counts["invalid_rows"] += 1
                    row = {"error_type": type(exc).__name__, "encoded_length": len(encoded),
                           "colon_count": encoded.count(":"), "expired": expiry <= now,
                           "expires_at": expiry.isoformat(), "has_binding": bound,
                           "binding_created_at": created.isoformat() if created else None,
                           "binding_expired": binding_expiry <= now if binding_expiry else None,
                           "binding_revoked": revoked, "group_revoked": group_revoked,
                           "empty_string": encoded == "", "literal_empty_json_object": encoded == "{}"}
                    # Treat unsigned JSON as untrusted forensic data, never as an authenticated session.
                    try:
                        value = json.loads(encoded)
                        row["unsigned_json_type"] = type(value).__name__
                        row["unsigned_json_empty_object"] = isinstance(value, dict) and not value
                        row["signals"] = signals(value)
                    except (ValueError, RecursionError):
                        row["unsigned_json_type"] = None
                        row["signals"] = signals(encoded)
                    try:
                        row["forensic_payload"] = inspect_untrusted_payload(encoded)
                    except Exception as payload_exc:
                        row["forensic_payload"] = {"status": "NOT_DECODED", "error_type": type(payload_exc).__name__}
                    report["invalid_rows"].append(row)
    report["counts"] = dict(counts)
    report["limitations"] = ["Unsigned data is not authenticated or restored into application sessions",
                             "No inference of test provenance from empty content alone"]
    folder = ROOT / "docs/validation/fr08-2026-11-23"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / ("session-diagnostics-" + now.strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
