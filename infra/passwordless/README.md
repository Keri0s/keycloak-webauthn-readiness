# Chuyển lab sang đăng nhập passwordless

Trạng thái (23/11/2026 20:53 UTC+7): Đã xác minh qua [`inspection.json`](../../docs/validation/passwordless-preflight/20261123T135327930466Z/inspection.json) và [bản đối chiếu cấu hình](../../docs/validation/passwordless-preflight/20261123T135327930466Z/review.md) rằng client `app-lab` gắn `client_override` tới flow `browser-passkey-uv` (`auth-username-form` REQUIRED + `webauthn-authenticator-passwordless` REQUIRED, `RP ID=auth.readiness.test`, `UV=required`). Đã ghi nhận các ca thực đăng ký (`UPDATE_CREDENTIAL` 22/11 và 23/11 09:47), đăng nhập (`LOGIN` 13:55/13:56/18:59:55/20:40:42 vào `/private/`) và ca hủy (`LOGIN_ERROR` 14:16 và 20:47:34) trong `evidence/ledger/so_bang_chung.csv`. Lỗi native Windows Security cần Try again giữ trạng thái `DEFERRED_OPEN`. Không dùng tài liệu thiết kế bên dưới làm bằng chứng đã kiểm thử mọi nhánh recovery/UV âm.

## Bước đang thực hiện: kiểm kê cấu hình thực tế

`inspect_keycloak.py` chỉ đọc cấu hình realm `webauthn-lab` và client `app-lab`
qua Admin REST API tại `https://auth.readiness.test:9443`. Nó xác minh TLS bằng
CA public của lab, không dùng proxy hệ thống, không theo redirect. POST duy nhất
là đăng nhập quản trị; các thao tác admin đều là GET. Việc đăng nhập có thể tạo
phiên/sự kiện quản trị trên Keycloak. Công cụ không đọc danh sách user/credential,
không xuất realm đầy đủ, không lưu mật khẩu/token, không thay flow hay policy.

Từ PowerShell tại thư mục gốc project:

```powershell
.\apps\lab\.venv\Scripts\python.exe .\infra\passwordless\inspect_keycloak.py
```

Nhập username quản trị của realm `master`, mật khẩu và OTP nếu có ngay trong
terminal. Hai trường sau nhập ẩn. Không gửi chúng vào chat hoặc ghi vào lệnh.
Nếu tài khoản không đăng nhập được bằng `admin-cli` (ví dụ chỉ dùng WebAuthn),
không tắt MFA/đổi policy để chạy công cụ. Dùng Admin Console và ghi lại các mục
trong bảng dưới. Không bật grant hoặc tạo thêm tài khoản quản trị chỉ vì công cụ.

Kết quả: `docs/validation/passwordless-preflight/<UTC>/inspection.json`.
Chỉ các trường được liệt kê rõ trong mã nguồn được xuất. File không phải bản
backup đủ để phục hồi realm, và không chứa secret của client.

| Dữ liệu cần đối chiếu | Mục đích |
| --- | --- |
| Realm Browser Flow và app-lab browser override | Tìm flow thực sự áp dụng |
| Executions và requirement trong các flow | Tìm password, OTP, cookie/SSO, broker và nhánh bỏ qua |
| WebAuthn Policy và WebAuthn Passwordless Policy | Phân biệt 2FA và passwordless; kiểm UV, RP ID, thuật toán |
| Required actions | Kiểm khả năng đăng ký credential đúng loại |
| Direct grants, implicit flow, reset password, self-registration | Xác định đường đăng nhập/cấp lại credential khác |
| Thời hạn phiên/action token và cờ events | Chuẩn bị kiểm thử hết hạn và thu bằng chứng |

Client policies, cấu hình bên trong custom authenticator, required-action max age,
Account Console, credential thực tế và quyền quản trị vẫn cần kiểm tra riêng.
Không tự kết luận an toàn chỉ từ danh sách executions hoặc UV = required.

Kiểm tra kết nối không cần tài khoản:

```powershell
.\apps\lab\.venv\Scripts\python.exe .\infra\passwordless\inspect_keycloak.py --check-connectivity
```

## Thiết kế sẽ chuyển thử sau kiểm kê

- Đăng nhập thường ngày: username + passkey, UV bắt buộc; không fallback mật khẩu/OTP.
- Thử flow mới trên client thử riêng trước khi thay app-lab nếu cấu hình cho phép.
  Không thay Browser Flow của realm ngay vì có thể ảnh hưởng Account Console và admin.
- Phiên Django hợp lệ vẫn dùng theo thời hạn hiện có. Khi đo FR-05, yêu cầu xác thực
  mới; không dùng phiên SSO từ bootstrap hoặc luồng cũ làm bằng chứng passkey.
- Đăng ký ban đầu: quản trị viên xác minh người nhận tài khoản lab, cấp quyền đăng
  ký có thời hạn. Cơ chế action link hay flow riêng sẽ chọn theo cấu hình thật.
  Không mặc định temporary password có TTL/one-time hoặc giới hạn quyền cần thiết.
- Chưa cho bootstrap truy cập `/private/`. Cần chứng minh quyền bootstrap không
  dùng được để lấy phiên nghiệp vụ, kể cả yêu cầu authorize trực tiếp.
- Thêm passkey: yêu cầu xác thực passkey mới, kiểm cả Account Console/AIA; chỉ
  `kc_action` hay một nút trên app không phải biện pháp bảo vệ đầy đủ.
- Mất mọi passkey: xác minh lại có quản trị viên, xử lý credential/phiên bị ảnh
  hưởng, cấp quyền đăng ký lại có thời hạn. Thử khả năng thu hồi phiên độc lập
  với xóa credential; không giả định xóa credential tự hủy mọi phiên.
- Giữ cấu hình trước chuyển đổi để phục hồi có kiểm soát; không mở luồng cũ làm
  fallback cho người dùng sau khi chuyển. Backup có secrets phải ở vùng local
  bị ignore, không đưa vào hồ sơ public.

Các mục này là thiết kế mục tiêu; chưa phải khả năng đã được kiểm chứng của runtime.

## Điều kiện trước khi chuyển app-lab

1. Xác định nguồn cấu hình, ảnh hưởng và cách phục hồi từng thay đổi.
2. Đăng ký credential đúng loại; thử đăng nhập mới thành công vào app (FR-04/05).
3. Từ chối thiếu UV, hủy, credential sai/đã thu hồi và tài khoản disabled;
   ghi rõ phép thử thật hay authenticator giả lập.
4. Đóng đường password/OTP/SSO cũ/khởi tạo có thể bỏ qua yêu cầu passkey.
5. Kiểm thêm passkey và recovery có đủ xác minh, thời hạn, chống dùng lại.
6. Thu sự kiện đúng nguồn cho FR-06/07; phân biệt timeout và người dùng hủy.
7. Chạy hồi quy phiên/logout liên quan; kiểm FR-08 rồi chấm lab bằng dữ liệu mới.

Giữ 19 ca SESSION_MAPPING_A và mã FR hiện có. Kiểm thử mới là bằng chứng bổ sung,
không tự cộng vào số ca đã nghiệm thu hoặc vào điểm readiness.

## Kiểm tra công cụ (offline)

```powershell
.\apps\lab\.venv\Scripts\python.exe -m unittest discover -s infra/passwordless -p "test_*.py" -v
```

Các test kiểm lọc dữ liệu, chọn client override, không theo redirect và không đọc
user/credential. Chúng không chứng minh Keycloak đã đăng nhập passwordless.

Nguồn đối chiếu đúng phiên bản khai báo trong Compose:
- [Keycloak 26.8.2 Server Administration](https://www.keycloak.org/docs/26.8.2/server_admin/index.html)
- [Keycloak 26.8.2 Admin REST API](https://www.keycloak.org/docs-api/26.8.2/rest-api/index.html)
