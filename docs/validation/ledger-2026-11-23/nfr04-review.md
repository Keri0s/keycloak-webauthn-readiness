# Rà soát NFR-04 và phụ lục FR-08 cho sổ bằng chứng (23/11/2026)

Tài liệu này chốt điểm xem sổ bằng chứng và kiểm tra yêu cầu **NFR-04 (Bằng chứng tối thiểu):** *"Sổ bằng chứng không hiện khóa riêng dù người xem là quản trị lab."*

---

## 1. Điểm xem và nguồn của sổ bằng chứng được chọn (IF-04 / NFR-04)

- **Nguồn sự kiện gốc:** Keycloak 26.8.2 Admin REST API (`GET /admin/realms/webauthn-lab/events`), đã cấu hình `eventsEnabled=true` trên realm `webauthn-lab`.
- **Sổ cấu trúc và điểm xem chính cho nghiệm thu:** tệp `evidence/ledger/so_bang_chung.csv` và giao diện dòng lệnh `python -m apps.ledger.cli show`.

---

## 2. Giải trình cơ chế không hiển thị khóa riêng ngay cả với quản trị viên lab

1. **Allowlist ở tầng schema (`apps/ledger/schema.py`):**
   - Danh sách cột lưu trữ `COLUMNS` (dòng 12–31) chỉ gồm 18 trường định danh, thời gian, tài khoản lab, thao tác, kết quả, `credential_type`, `credential_id`, `credential_label`, `uv_checked`, `registration_context`, `source_event_type`, `error_code`, `webauthn_error`, `session_ref`, `subject_ref`, `pulled_at_utc`.
   - Danh sách hiển thị bảng `DISPLAY_COLUMNS` (dòng 33–45) là tập con 11 trường (kèm giờ UTC+7 quy đổi từ `occurred_at_utc`).
   - Tuyệt đối không khai báo trường cho khóa riêng (`privateKey`, `private_key`, `pkcs8`, `jwk.d`), `secret_data`, `ipAddress`, `sessionId` thô, `userId` thô, `code_id`, `redirect_uri`, token, cookie hay payload WebAuthn thô.

2. **Lọc allowlist ở tầng ánh xạ (`apps/ledger/mapping.py`):**
   - Hàm `event_to_row()` (dòng 89–167) chỉ đọc đúng 7 khóa được phép từ `event["details"]` (`username`, `credential_type`, `public_key_credential_id`, `public_key_credential_label`, `web_authn_authenticator_user_verification_checked`, `custom_required_action`, `web_authn_authentication_error`/`web_authn_registration_error`). Mọi trường lạ trong `details` đều bị bỏ qua.
   - `error_code` và `webauthn_error` được kiểm tra qua regex `^[A-Za-z0-9_.-]{1,80}$` (`_normalize_code`), tránh ghi chuỗi mô tả lỗi tự do.
   - `session_ref` và `subject_ref` là mã băm SHA-256 hex, không lưu giá trị gốc.

3. **Lọc lại khi đọc, lưu và hiển thị (`apps/ledger/store.py`, `apps/ledger/cli.py`):**
   - `load_rows()` và `save_rows()` trong `apps/ledger/store.py` gọi `_sanitize_row()` để chỉ giữ các cột trong `COLUMNS` và dùng `csv.DictWriter(..., extrasaction="ignore")`.
   - `cmd_show()` trong `apps/ledger/cli.py` chỉ đọc qua `load_rows()` và in theo `DISPLAY_COLUMNS` hoặc `COLUMNS` (khi dùng `--id`). Không có cờ CLI (`--raw`, `--all`, `--admin`) cho phép quản trị viên lab xem trường ngoài allowlist.

4. **Kiểm chứng offline bằng unit test (`apps/ledger/tests/`):**
   - `test_disallowed_details_and_ip_address_are_dropped` (`test_mapping.py`): chèn `privateKey`, `code_id`, `redirect_uri`, `attestationObject`, `ipAddress`, `sessionId` thô vào event đầu vào → xác nhận không xuất hiện trong kết quả ánh xạ.
   - `test_save_and_load_drop_disallowed_columns_including_private_key` (`test_store.py`) và `test_show_excludes_disallowed_csv_column_and_supports_filters` (`test_cli_show.py`): chèn trực tiếp cột `private_key` vào tệp CSV trên đĩa → xác nhận `load_rows`, `save_rows` và `cli.py show` (cả dạng bảng lẫn `--id`) đều loại bỏ và không in ra.

---

## 3. Liên hệ kiến trúc WebAuthn và kết quả FR-08 đã có

- Theo chuẩn WebAuthn, khóa riêng của passkey nằm trong authenticator/thiết bị người dùng và không được gửi về máy chủ trong giao thức đăng ký/xác thực.
- Ở tầng lưu trữ Keycloak (`docs/validation/fr08-2026-11-23/report.md`), truy vấn DB chỉ đọc đã xác nhận 2 credential `webauthn-passwordless` trong realm `webauthn-lab` có `secret_data` object rỗng và `credential_data` chỉ gồm `aaguid`, `attestationStatementFormat`, `counter`, `credentialId`, `credentialPublicKey`, `transports`; đồng thời 67 event thuộc 4 loại trong 2 cột JSON và 461 dòng log container Keycloak/Caddy đều có bộ đếm marker khóa riêng bằng `0`.

## Cập nhật đối chiếu sổ live — 23/11/2026 14:04 UTC (21:04 UTC+7)

Sau khi người dùng chạy Mục A–C trong [runbook](runbook.md) tạo `evidence/ledger/so_bang_chung.csv` (67 dòng, 20.054 byte, SHA-256 `fca424aaf19fd59fc2ad9a759aaac685c103c0687fb5dd9c2d19a58192bae80f`) và `evidence/ledger/pull-log.jsonl` (5 lần pull, 3.175 byte, SHA-256 `34ae201fbd352b0a3d71256b43756392c5efaa1b3e2d8f968041d5d9b28b2448`):
- Đã chạy `.\apps\lab\.venv\Scripts\python.exe .\infra\passwordless\audit_fr08_exports.py`: tất cả bộ đếm `private_named_fields`, `private_jwk_objects`, `text_markers` trên cả hai tệp đều bằng `0` (`flagged_paths = []`).
- Xác nhận trực tiếp bằng kiểm tra nội dung CSV và đầu ra `apps.ledger.cli show --id`: không có `privateKey`, IP (`172.21.0.1`), `code_id`, `redirect_uri` hoặc chuỗi mô tả lỗi tự do (`NotAllowedError: The operation...`) trong sổ lưu trữ lẫn đầu ra hiển thị.

## Giới hạn

- Bộ dò heuristic kiểm tra dấu hiệu khóa riêng đã biết, không thay thế kiểm chứng mọi dạng mã hóa tùy biến; kết quả áp dụng cho 67 dòng sự kiện trong sổ và 62 tệp JSON/JSONL/CSV đã quét trong phạm vi công bố.
