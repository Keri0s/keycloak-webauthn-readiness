"""Unit tests for CLI show command filtering and allowlisted output."""
from __future__ import annotations

from contextlib import redirect_stdout
import csv
import io
from pathlib import Path
import tempfile
import unittest

from apps.ledger.cli import main
from apps.ledger.mapping import event_to_row
from apps.ledger.schema import COLUMNS


class CliShowTests(unittest.TestCase):
    def test_show_excludes_disallowed_csv_column_and_supports_filters(self):
        login_row = event_to_row(
            {
                "id": "evt-login-1",
                "time": 1795435195655,  # 2026-11-23T11:59:55.655Z
                "type": "LOGIN",
                "realmId": "webauthn-lab",
                "clientId": "app-lab",
                "userId": "uid-1",
                "details": {
                    "username": "lab-user-01",
                    "credential_type": "webauthn-passwordless",
                    "public_key_credential_id": "gGCUOjoWoGQwWgLe3SMDow",
                    "web_authn_authenticator_user_verification_checked": "true",
                },
            },
            pulled_at="2026-11-23T12:05:00.000Z",
        )
        cancel_row = event_to_row(
            {
                "id": "evt-cancel-1",
                "time": 1795418160000,  # 2026-11-23T07:16:00.000Z
                "type": "LOGIN_ERROR",
                "realmId": "webauthn-lab",
                "clientId": "app-lab",
                "userId": None,
                "error": "not_allowed",
                "details": {"credential_type": "webauthn-passwordless"},
            },
            pulled_at="2026-11-23T12:05:00.000Z",
        )
        assert login_row is not None and cancel_row is not None

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "so_bang_chung.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(COLUMNS) + ["private_key"])
                writer.writeheader()
                writer.writerow({**cancel_row, "private_key": "FORBIDDEN_SECRET_KEY"})
                writer.writerow({**login_row, "private_key": "FORBIDDEN_SECRET_KEY"})

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["show", "--ledger", str(csv_path)])
            out = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn("evt-login-1", out)
            self.assertIn("evt-cancel-1", out)
            self.assertNotIn("private_key", out)
            self.assertNotIn("FORBIDDEN_SECRET_KEY", out)

            # Filter by outcome=failure
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["show", "--outcome", "failure", "--ledger", str(csv_path)])
            self.assertEqual(rc, 0)
            self.assertIn("evt-cancel-1", buf.getvalue())
            self.assertNotIn("evt-login-1", buf.getvalue())

            # Filter by --since (UTC+7 timestamp after cancel, before login)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    ["show", "--since", "2026-11-23T18:00:00+07:00", "--ledger", str(csv_path)]
                )
            self.assertEqual(rc, 0)
            self.assertIn("evt-login-1", buf.getvalue())
            self.assertNotIn("evt-cancel-1", buf.getvalue())

            # Single-record detail via --id (NFR-03)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["show", "--id", "evt-login-1", "--ledger", str(csv_path)])
            detail_out = buf.getvalue()
            self.assertEqual(rc, 0)
            for col in COLUMNS:
                self.assertIn(col + ":", detail_out)
            self.assertNotIn("private_key", detail_out)
            self.assertNotIn("FORBIDDEN_SECRET_KEY", detail_out)


if __name__ == "__main__":
    unittest.main()
