# Sổ bằng chứng WebAuthn (`apps/ledger`)

Sổ bằng chứng cấu trúc cho **FR-06, FR-07, IF-04, DR-03 và NFR-04** trong đồ án N15.

## Mục đích và nguồn dữ liệu

- **Nguồn gốc:** Keycloak 26.8.2 Admin REST API (`GET /admin/realms/webauthn-lab/events`), lọc cứng theo realm `webauthn-lab` và client `app-lab`.
- **Điểm lưu và xem chính:** tệp CSV `evidence/ledger/so_bang_chung.csv`, nhật ký mỗi lần kéo `evidence/ledger/pull-log.jsonl`, và giao diện CLI `python -m apps.ledger.cli show`.
- **Tách biệt với sổ mẫu:** không thay thế hoặc sửa `DU_LIEU_MAU/N15_San_sang_WebAuthn/so_bang_chung_mau.csv`.

## Các cột của sổ (allowlist cố định)

`COLUMNS` trong [schema.py](schema.py) chỉ gồm:
`evidence_id`, `occurred_at_utc`, `realm`, `client_id`, `lab_account`, `operation`, `outcome`, `credential_type`, `credential_id`, `credential_label`, `uv_checked`, `registration_context`, `source_event_type`, `error_code`, `webauthn_error`, `session_ref`, `subject_ref`, `pulled_at_utc`.

Không lưu và không hiển thị (ngay cả khi người chạy là quản trị viên lab): `ipAddress`, `sessionId` thô, `userId` thô, `code_id`, `redirect_uri`, access/refresh/ID token, cookie, raw WebAuthn response (`clientDataJSON`, `authenticatorData`, `signature`), `publicKey`, `attestation`, hay bất kỳ `privateKey` nào.

- `session_ref` và `subject_ref` là SHA-256 hex theo cùng công thức với `apps/lab/authn/evidence.py` và `infra/passwordless/fr05-login.sql` để đối chiếu lượt vào `/private/` mà không lưu SID/UID gốc.

## Quy tắc ca hủy / thất bại (FR-07)

- `LOGIN_ERROR` ánh xạ thành `operation=authentication`, `outcome=failure`.
- Nếu `userId` không có (`No user details`) và `details.username` không có, `lab_account` ghi `unknown`. **Không** suy đoán từ lần đăng nhập trước.
- Nếu sự kiện không có `public_key_credential_id`, `credential_id` để trống; **không** gán credential từ lần thành công khác.
- Chuỗi mô tả lỗi tự do trong `details` không được lưu nguyên văn; `error_code` và `webauthn_error` chỉ giữ mã ký tự an toàn (`^[A-Za-z0-9_.-]{1,80}$`), ngược lại ghi `other`.

## Giới hạn đã biết

- Chỉ lấy `LOGIN`, `LOGIN_ERROR`, `UPDATE_CREDENTIAL`, `UPDATE_CREDENTIAL_ERROR` của `app-lab`.
- **Không** đếm `CUSTOM_REQUIRED_ACTION` để tránh trùng với `UPDATE_CREDENTIAL`, và **không** đếm `CODE_TO_TOKEN` thành lượt đăng nhập thứ hai.
- Realm lab hiện cấu hình lưu sự kiện `7 ngày` (`eventsExpiration=604800`); cần chạy `pull` trước khi sự kiện hết hạn trên Keycloak.
- Lệnh `show` chỉ đọc CSV hiện có và bỏ qua mọi cột ngoài `COLUMNS`.

## Lệnh chạy (dùng venv của lab vì có `requests`)

Từ thư mục gốc `D:\Projects\Do-an-thuctap-totnghiep`:

```powershell
# Kéo sự kiện từ Keycloak (nhập tài khoản admin realm master trực tiếp trong terminal)
.\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli pull --since 2026-11-16

# Xem toàn bộ bảng bằng chứng
.\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli show

# Lọc hoặc mở đúng một dòng bằng chứng (NFR-03)
.\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli show --operation authentication --outcome failure
.\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli show --id <evidence_id>
```

## Kiểm thử offline

```powershell
.\apps\lab\.venv\Scripts\python.exe -m unittest discover -s apps/ledger/tests -t . -v
```
