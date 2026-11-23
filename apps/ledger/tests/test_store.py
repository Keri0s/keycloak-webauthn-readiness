"""Unit tests for CSV store deduplication, atomic write, and column allowlisting."""
from __future__ import annotations

import csv
from pathlib import Path
import tempfile
import unittest

from apps.ledger.mapping import event_to_row
from apps.ledger.schema import COLUMNS
from apps.ledger.store import load_rows, merge, save_rows


class LedgerStoreTests(unittest.TestCase):
    def _sample_row(self, ev_id: str, time_ms: int) -> dict[str, str]:
        row = event_to_row(
            {
                "id": ev_id,
                "time": time_ms,
                "type": "LOGIN",
                "realmId": "webauthn-lab",
                "clientId": "app-lab",
                "userId": "uid-1",
                "details": {
                    "username": "lab-user-01",
                    "credential_type": "webauthn-passwordless",
                    "public_key_credential_id": "gGCUOjoWoGQwWgLe3SMDow",
                },
            },
            pulled_at="2026-11-23T12:05:00.000Z",
        )
        assert row is not None
        return row

    def test_merge_deduplicates_repeat_pull_and_keeps_same_minute_events(self):
        row1 = self._sample_row("evt-a", 1795435140000)  # same minute
        row2 = self._sample_row("evt-b", 1795435185000)  # same minute, later sec

        merged1, added1, dup1 = merge([], [row2, row1])
        self.assertEqual((added1, dup1), (2, 0))
        self.assertEqual([r["evidence_id"] for r in merged1], ["evt-a", "evt-b"])

        # Repeat pull of the exact same batch adds 0 and reports 2 duplicates.
        merged2, added2, dup2 = merge(merged1, [row1, row2])
        self.assertEqual((added2, dup2), (0, 2))
        self.assertEqual(len(merged2), 2)

    def test_save_and_load_drop_disallowed_columns_including_private_key(self):
        row = self._sample_row("evt-clean", 1795435195655)
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "so_bang_chung.csv"
            # Manually write CSV containing an extra disallowed column 'private_key'.
            fieldnames = list(COLUMNS) + ["private_key"]
            with csv_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({**row, "private_key": "LEAKED_PRIVATE_KEY_VALUE"})

            loaded = load_rows(csv_path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(tuple(loaded[0].keys()), COLUMNS)
            self.assertNotIn("private_key", loaded[0])
            self.assertNotIn("LEAKED_PRIVATE_KEY_VALUE", " ".join(loaded[0].values()))

            # Re-saving strips any unknown keys cleanly.
            save_rows(csv_path, [{**row, "private_key": "SHOULD_NOT_WRITE"}])
            raw_text = csv_path.read_text(encoding="utf-8")
            self.assertNotIn("private_key", raw_text)
            self.assertNotIn("SHOULD_NOT_WRITE", raw_text)


if __name__ == "__main__":
    unittest.main()
