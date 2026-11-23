# Hồ sơ bằng chứng FR-04 — Đăng ký passkey

- **Yêu cầu (SRS 3.2, FR-04):** *"Tài khoản lab đăng ký được một passkey trên realm Keycloak lab."* (Mức: Bắt buộc)
- **Phương thức kiểm tra theo SRS:** `Demo`
- **Trạng thái hiện tại:** `Đã quan sát` (theo đối chiếu 23/11/2026)

## Bằng chứng hiện có
- Quan sát giao diện đăng ký passwordless ngày 22/11/2026 (`PL-REG-01`–`PL-REG-03`): [`docs/validation/passwordless-enrollment-2026-11-22/report.md`](../../docs/validation/passwordless-enrollment-2026-11-22/report.md).
- Quan sát sự kiện `UPDATE_CREDENTIAL` ngày 23/11/2026 lúc `09:47` cho `lab-user-01`, client `app-lab`, `credential_type=webauthn-passwordless`, `custom_required_action=webauthn-register-passwordless`, `public_key_credential_id=gGCUOjoWoGQwWgLe3SMDow`: [`docs/validation/callback-recovery-2026-11-23/registration-event-0947.md`](../../docs/validation/callback-recovery-2026-11-23/registration-event-0947.md).
- Dữ liệu kéo về sổ cấu trúc [`evidence/ledger/so_bang_chung.csv`](../ledger/so_bang_chung.csv) ([báo cáo sổ live](../../docs/validation/ledger-2026-11-23/report.md)): đã lưu cả 2 sự kiện đăng ký `UPDATE_CREDENTIAL` (`52a3a562-b588-4713-8352-bedadb8929ff` ngày 22/11 `dndRW6XS6qIJg61vLgTUVw` và `165052bf-adf9-4cac-b04f-f73fd25a480e` ngày 23/11 `gGCUOjoWoGQwWgLe3SMDow`).

## Giới hạn
- Ảnh gốc hiện nằm trong lịch sử hội thoại, chưa sao chép trực tiếp vào thư mục này.
- Bằng chứng hiện ghi nhận ca đăng ký thực hiện thành công của `lab-user-01`; chưa kiểm chứng toàn bộ nhánh khôi phục hoặc cấp lại khi mất tất cả passkey.

## Ảnh người dùng cần tự lưu vào thư mục này
1. Ảnh màn hình đăng ký passkey thành công ngày 22/11 (hộp thoại Windows Security / thông báo `Passkey saved`, đã che query phiên nếu có).
2. Ảnh tab **Credentials** của tài khoản `lab-user-01` trong Keycloak Admin Console (`Webauthn-passwordless`, nhãn `Edge-Passkey` / `Passkey (Default Label)`).
3. Ảnh chi tiết sự kiện `UPDATE_CREDENTIAL` lúc `09:47` ngày 23/11 (đã che `code_id` / IP nếu cần).
4. Đầu ra `.\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli show --operation registration` từ dữ liệu đã kéo trong [`so_bang_chung.csv`](../ledger/so_bang_chung.csv).
