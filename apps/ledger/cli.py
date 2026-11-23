"""CLI for pulling and viewing the N15 WebAuthn evidence ledger."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
from getpass import getpass
from pathlib import Path
import sys
from typing import Sequence

from apps.ledger.mapping import event_to_row
from apps.ledger.schema import COLUMNS, DISPLAY_COLUMNS
from apps.ledger.store import (
    append_pull_log,
    compute_ledger_hashes,
    load_rows,
    merge,
    save_rows,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER_PATH = ROOT / "evidence/ledger/so_bang_chung.csv"
DEFAULT_PULL_LOG_PATH = ROOT / "evidence/ledger/pull-log.jsonl"
VN_TZ = timezone(timedelta(hours=7))


def _utc_now_ms() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def _format_vn_time(occurred_at_utc: str) -> str:
    if not occurred_at_utc:
        return ""
    try:
        dt = datetime.fromisoformat(occurred_at_utc).astimezone(VN_TZ)
        return dt.strftime("%Y-%m-%d %H:%M:%S+07:00")
    except ValueError:
        return ""


def _parse_since_utc(value: str) -> datetime:
    stripped = value.strip()
    if len(stripped) == 10:
        date.fromisoformat(stripped)
        return datetime.fromisoformat(stripped + "T00:00:00+00:00")
    parsed = datetime.fromisoformat(stripped)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def cmd_pull(args: argparse.Namespace) -> int:
    from apps.ledger.keycloak import CA, LabEventsClient, LedgerAPIError
    import requests

    since_str = args.since or (datetime.now(VN_TZ).date() - timedelta(days=7)).isoformat()
    try:
        date.fromisoformat(since_str)
    except ValueError:
        print(f"Ngày --since không hợp lệ (cần YYYY-MM-DD): {since_str}")
        return 1

    if not CA.is_file():
        print("Thiếu CA public của lab: infra/.runtime/keycloak-trust/readiness-root.pem")
        return 1

    if not sys.stdin.isatty():
        print("Hãy chạy pull trực tiếp trong terminal tương tác; không pipe mật khẩu.")
        return 1

    print("Nhập tài khoản quản trị Keycloak (realm master; không lưu mật khẩu):")
    username = input("Admin username: ").strip()
    if not username or "python.exe" in username.lower():
        print("Tên đăng nhập không hợp lệ.")
        return 1
    password = getpass("Admin password (hidden; not saved): ")
    otp = getpass("Admin OTP if configured (otherwise Enter): ")

    client = LabEventsClient()
    pulled_at = _utc_now_ms()
    try:
        client.authenticate(username, password, otp)
        realm_id = client.realm_id()
        raw_events = client.events(since_str)
        mapped_rows: list[dict[str, str]] = []
        for event in raw_events:
            row = event_to_row(
                event,
                username_lookup=client.username,
                pulled_at=pulled_at,
                expected_realm_id=realm_id,
            )
            if row is not None:
                mapped_rows.append(row)
    except (LedgerAPIError, ValueError, requests.RequestException) as exc:
        if isinstance(exc, (LedgerAPIError, ValueError)):
            print(f"Pull dừng lại: {exc}")
        else:
            print("Pull dừng lại: lỗi kết nối HTTPS tới lab Keycloak.")
        return 1
    finally:
        del password, otp
        client.close()

    ledger_path = Path(args.ledger)
    pull_log_path = ledger_path.parent / "pull-log.jsonl"
    existing = load_rows(ledger_path)
    merged, added, duplicates = merge(existing, mapped_rows)
    save_rows(ledger_path, merged)
    append_pull_log(
        pull_log_path,
        {
            "pulled_at": pulled_at,
            "window": {"since": since_str},
            "fetched": len(raw_events),
            "mapped": len(mapped_rows),
            "added": added,
            "duplicates": duplicates,
            "total_rows": len(merged),
            "tool_sha256": compute_ledger_hashes(ROOT),
        },
    )
    print(
        f"Hoàn tất pull từ {since_str}: fetched={len(raw_events)}, "
        f"mapped={len(mapped_rows)}, added={added}, duplicates={duplicates}, total={len(merged)}"
    )
    print(f"Sổ bằng chứng: {ledger_path}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    ledger_path = Path(args.ledger)
    rows = load_rows(ledger_path)

    if args.id:
        matches = [r for r in rows if r["evidence_id"] == args.id]
        if not matches:
            print(f"Không tìm thấy evidence_id={args.id} trong {ledger_path}")
            return 1
        row = matches[0]
        print(f"Chi tiết dòng bằng chứng ({ledger_path}):")
        for col in COLUMNS:
            print(f"  {col}: {row[col]}")
        print(f"  occurred_at_vn: {_format_vn_time(row['occurred_at_utc'])}")
        return 0

    since_dt: datetime | None = None
    if args.since:
        try:
            since_dt = _parse_since_utc(args.since)
        except ValueError:
            print(f"Giá trị --since không hợp lệ: {args.since}")
            return 1

    filtered: list[dict[str, str]] = []
    for row in rows:
        if args.operation and row["operation"] != args.operation:
            continue
        if args.outcome and row["outcome"] != args.outcome:
            continue
        if since_dt is not None:
            try:
                row_dt = datetime.fromisoformat(row["occurred_at_utc"]).astimezone(timezone.utc)
            except ValueError:
                continue
            if row_dt < since_dt:
                continue
        filtered.append(row)

    if not filtered:
        print(f"Không có dòng bằng chứng phù hợp trong {ledger_path}.")
        return 0

    display_rows = []
    for row in filtered:
        item = {col: row.get(col, "") for col in DISPLAY_COLUMNS}
        item["occurred_at_vn"] = _format_vn_time(row["occurred_at_utc"])
        display_rows.append(item)

    widths = {
        col: max(len(col), *(len(r[col]) for r in display_rows))
        for col in DISPLAY_COLUMNS
    }
    header = " | ".join(col.ljust(widths[col]) for col in DISPLAY_COLUMNS)
    print(header)
    print("-+-".join("-" * widths[col] for col in DISPLAY_COLUMNS))
    for item in display_rows:
        print(" | ".join(item[col].ljust(widths[col]) for col in DISPLAY_COLUMNS))
    print(f"\nTổng cộng: {len(display_rows)} dòng.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sổ bằng chứng WebAuthn N15 (lấy từ Keycloak Admin Events và hiển thị theo allowlist)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pull_p = sub.add_parser("pull", help="Kéo sự kiện từ Keycloak lab về sổ CSV")
    pull_p.add_argument(
        "--since",
        default=None,
        help="Ngày bắt đầu YYYY-MM-DD (mặc định: 7 ngày trước theo UTC+7)",
    )
    pull_p.add_argument(
        "--ledger",
        default=str(DEFAULT_LEDGER_PATH),
        help="Đường dẫn file CSV sổ bằng chứng (mặc định: evidence/ledger/so_bang_chung.csv)",
    )

    show_p = sub.add_parser("show", help="Xem sổ bằng chứng theo danh sách trường cho phép")
    show_p.add_argument(
        "--operation",
        choices=("registration", "authentication"),
        default=None,
        help="Lọc theo loại thao tác",
    )
    show_p.add_argument(
        "--outcome",
        choices=("success", "failure"),
        default=None,
        help="Lọc theo kết quả",
    )
    show_p.add_argument(
        "--since",
        default=None,
        help="Lọc sự kiện từ thời điểm ISO-8601 hoặc YYYY-MM-DD",
    )
    show_p.add_argument(
        "--id",
        default=None,
        help="Mở chi tiết đúng một dòng theo evidence_id",
    )
    show_p.add_argument(
        "--ledger",
        default=str(DEFAULT_LEDGER_PATH),
        help="Đường dẫn file CSV sổ bằng chứng",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "pull":
        return cmd_pull(args)
    if args.command == "show":
        return cmd_show(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
