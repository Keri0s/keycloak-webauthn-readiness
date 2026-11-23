# Hồ sơ bằng chứng FR-07 — Bằng chứng thất bại

- **Yêu cầu (SRS 3.2, FR-07):** *"Một lần đăng nhập passkey bị hủy tạo dòng kết quả thất bại, không có khóa riêng."* (Mức: Bắt buộc)
- **Phương thức kiểm tra theo SRS:** `Kiểm thử`
- **Trạng thái hiện tại:** `Đã quan sát` (ca hủy `14:16` và ca hủy Mục C `20:47:34` ngày 23/11 đã ghi nhận vào `so_bang_chung.csv` + unit test offline PASS)

## Bằng chứng hiện có
- Ca hủy Mục C ngày 23/11 lúc `20:47:34+07:00`: [`docs/validation/ledger-2026-11-23/report.md`](../../docs/validation/ledger-2026-11-23/report.md) — thao tác hủy tạo sự kiện Keycloak `LOGIN_ERROR` (`error=not_allowed`, `web_authn_authentication_error=webauthn-error-api-not-allowed`), truy cập `/private/` nhận HTTP `403 Forbidden`; lệnh `pull` thêm đúng 1 dòng mới (`added=1`, `total=67`) `evidence_id=0bf7d697-a7c6-4d95-9e22-f60c2402dd31` trong [`evidence/ledger/so_bang_chung.csv`](../ledger/so_bang_chung.csv) với `lab_account=unknown`, `operation=authentication`, `outcome=failure`, `credential_id=""`, không chứa IP, `code_id`, mô tả lỗi dài hay khóa riêng.
- Ca hủy thủ công ngày 23/11 lúc `14:16`: [`docs/validation/callback-recovery-2026-11-23/cancel-event-1416.md`](../../docs/validation/callback-recovery-2026-11-23/cancel-event-1416.md).
- Kiểm thử mapping trong `apps/ledger/tests/test_mapping.py`: `test_login_error_null_user_and_long_detail_does_not_leak_description`.

## Giới hạn
- Sự kiện `LOGIN_ERROR` của ca hủy thường không có `userId` hay `public_key_credential_id` do hủy trước khi chọn/ký credential; sổ ghi `lab_account=unknown` và để trống `credential_id` thay vì suy đoán từ lần đăng nhập trước.

## Ảnh người dùng cần tự lưu vào thư mục này
1. Bộ 4 ảnh ca hủy 14:16 (hộp thoại Windows Security, trang Passkey Error, chi tiết sự kiện `LOGIN_ERROR` trên Keycloak Events, và trang Chrome `/private/` báo `403 Forbidden`; đã che IP/`code_id`/query nếu có).
2. Bộ ảnh Mục C ngày 23/11 (ảnh Events `LOGIN_ERROR` 8:47 PM đã che IP/`code_id`, ảnh `pull` + `show --outcome failure`, ảnh `/private/` `403 Forbidden`).
