# Hướng dẫn thu dữ liệu thực tế cho sổ bằng chứng (23/11/2026)

Tài liệu này hướng dẫn các thao tác **live** với Keycloak lab (`https://auth.readiness.test:9443`) và app Django (`https://app.readiness.test:9443`) để hoàn thiện bằng chứng thực tế cho **FR-06, FR-07, IF-04, DR-03, NFR-02, NFR-03, NFR-04**.

> [!IMPORTANT]
> Hãy chạy **Mục A trước ngày 29/11/2026** vì realm `webauthn-lab` đang cấu hình `eventsExpiration=604800` (7 ngày); các sự kiện ngày 22–23/11 sẽ bị xóa tự động khi quá 7 ngày.
> Không gửi mật khẩu, OTP, cookie, `code=` hoặc query string phiên vào chat.

---

## Điều kiện trước khi chạy

1. Docker Compose tại `infra/` đang chạy (`keycloak`, `keycloak-db`, `app-db`, `caddy`).
2. Ứng dụng Django tại `apps/lab` đang chạy trên cổng `18000` (đã nạp code mới có header đối chiếu `/private/`).
3. Chạy mọi lệnh dưới đây trong PowerShell tương tác từ thư mục gốc `D:\Projects\Do-an-thuctap-totnghiep`.

---

## A. Kéo các sự kiện lịch sử 22–23/11 về sổ (Khẩn)

Chạy lệnh sau và nhập tài khoản quản trị realm `master` trực tiếp trong terminal:

```powershell
.\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli pull --since 2026-11-16
.\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli show
```

**Expected:**
- Bảng `show` hiển thị được các sự kiện của `app-lab` từ ngày 22–23/11 (bao gồm `UPDATE_CREDENTIAL` 09:47 ngày 23/11, các lượt `LOGIN` 13:55/13:56/18:59:55 và các `LOGIN_ERROR` 14:16/20:05 nếu vẫn còn trong cửa sổ 7 ngày).
- Gửi lại kết quả text của lệnh `pull` và `show` (có thể che bớt nếu không có giá trị nhạy cảm; sổ mặc định đã ẩn IP/SID/UID thô).

---

## B. Kiểm thử FR-06: đăng nhập thành công → có đúng 1 dòng mới và không trùng khi kéo lại

1. Chạy `pull` làm mốc baseline và ghi lại số `total`:

   ```powershell
   .\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli pull --since 2026-11-23
   ```

2. Ghi nhận mốc thời gian hiện tại theo giờ Việt Nam (ví dụ `2026-11-23T20:00:00+07:00`).
3. Trên trình duyệt Edge: nếu đang đăng nhập, bấm **Đăng xuất** tại `https://app.readiness.test:9443/private/`. Sau đó mở mới `https://app.readiness.test:9443/auth/login/` và đăng nhập `lab-user-01` bằng passkey + PIN.
4. Khi vào `https://app.readiness.test:9443/private/` (HTTP 200), mở **DevTools → Network** (chọn request `/private/` → **Response Headers**) và ghi lại giá trị `X-Lab-Session-Ref` và `X-Lab-Subject-Ref`.
5. Quay lại PowerShell, chạy `pull` và lọc bằng `--since`:

   ```powershell
   .\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli pull --since 2026-11-23
   .\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli show --since <MỐC_THỜI_GIAN_ISO_VỪA_GHI>
   ```

   **Expected:**
   - Xuất hiện đúng **1** dòng mới với `operation=authentication`, `outcome=success`, `source_event_type=LOGIN`, `credential_id=gGCUOjoWoGQwWgLe3SMDow`.
   - Mở chi tiết dòng đó bằng `.\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli show --id <evidence_id>` và đối chiếu `session_ref` khớp với header `X-Lab-Session-Ref` ở bước 4.

6. Kiểm tra chống trùng lặp khi kéo lại (idempotency): chạy `pull` thêm 1 lần ngay sau đó:

   ```powershell
   .\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli pull --since 2026-11-23
   ```

   **Expected:** `added=0`, `duplicates=<số sự kiện đã có>`, không tạo dòng trùng.

---

## C. Kiểm thử FR-07: hủy hộp thoại passkey → có dòng thất bại mới trong sổ

1. Đăng xuất khỏi `https://app.readiness.test:9443/private/` (nếu đang đăng nhập). Ghi lại mốc thời gian bắt đầu thử (ví dụ `2026-11-23T20:05:00+07:00`).
2. Mở mới `https://app.readiness.test:9443/auth/login/`, nhập `lab-user-01`, bấm **Sign in with Passkey**, rồi bấm **Cancel** trên hộp thoại Windows Security.
3. Thử mở `https://app.readiness.test:9443/private/` trong cùng trình duyệt.
   **Expected:** nhận HTTP `403` (bị từ chối truy cập).
4. Quay lại PowerShell, kéo và lọc các dòng thất bại:

   ```powershell
   .\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli pull --since 2026-11-23
   .\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli show --outcome failure --since <MỐC_THỜI_GIAN_C>
   ```

   **Expected:** có đúng 1 dòng mới với `operation=authentication`, `outcome=failure`, `source_event_type=LOGIN_ERROR`, `error_code=not_allowed` (hoặc mã tương ứng), `lab_account=unknown` (nếu event Keycloak ghi `No user details`), `credential_id` để trống.

---

## D. Cập nhật đối chiếu cấu hình hiệu lực (NFR-02 / NFR-03)

Chạy lại công cụ kiểm kê cấu hình để lưu bản `inspection.json` phản ánh `effective_browser_flow` và chính sách passwordless hiện hành (bản trước đó thuộc ngày 22/11 trước khi gắn luồng mới):

```powershell
.\apps\lab\.venv\Scripts\python.exe .\infra\passwordless\inspect_keycloak.py
```

---

## Ghi chú về lỗi native Try again

- Lỗi Windows Security xuất hiện phải bấm *Try again* tiếp tục giữ trạng thái **DEFERRED_OPEN** theo quyết định trước đó.
- Nếu hiện tượng này xảy ra trong lúc thực hiện Mục B, chỉ cần ghi lại số lần bấm *Try again* (nếu có) để ghi nhận vào giới hạn thực nghiệm; hiện tượng này không làm vô hiệu hóa kết quả đối chiếu sổ bằng chứng.
