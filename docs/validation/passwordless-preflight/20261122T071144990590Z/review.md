# Đối chiếu cấu hình — 22/11/2026

Nguồn: `inspection.json` cùng thư mục, thu lúc 07:11:44 UTC bởi người dùng;
trợ lý đã đọc file. Đây là kiểm tra cấu hình, không phải nghiệm thu đăng nhập.

| Thành phần | Quan sát |
| --- | --- |
| app-lab | Không có browser override, dùng realm browser-password-webauthn |
| Nhánh forms | Username Password Form REQUIRED, subflow 2FA REQUIRED, WebAuthn Authenticator REQUIRED |
| Nhánh khác | Cookie ALTERNATIVE; Identity Provider Redirector và Organization còn trong flow |
| Policy WebAuthn thường | RP ID auth.readiness.test, UV required, attachment platform |
| Policy passwordless | UV required; RP ID rỗng; attachment và resident key not specified |
| Đăng ký passwordless | webauthn-register-passwordless enabled, defaultAction false |
| Client grants | Standard flow bật; implicit/direct grants/service accounts tắt; PKCE S256 |
| Cấp tài khoản/khôi phục | Self-registration và reset password tắt |
| Events | User events bật, giữ 604800 giây; admin events tắt |
| Admin action token | Realm lifespan 43200 giây; chưa có quyết định TTL riêng cho bootstrap |

Flow forms hiện tại sử dụng mật khẩu + WebAuthn thường, chưa chứa passwordless
authenticator. UV required của policy passwordless không chứng minh app sử dụng
policy này. RP ID rỗng chưa đủ kết luận lỗi: cần đối chiếu giá trị hiệu lực/default;
thiết kế mới sẽ đặt tường minh auth.readiness.test.

Chưa đọc credential user, client policies hay cấu hình chi tiết của custom provider;
không suy đoán các nhánh broker/organization có thể dùng được chỉ từ sự hiện diện.
Không coi createTimeout = 0 là challenge không hết hạn; cần kiểm phía server riêng.

Bước kế tiếp: tạo flow basic mới tên `browser-passkey-uv` chưa bind, gồm Username
Form REQUIRED rồi WebAuthn Passwordless Authenticator REQUIRED. Giai đoạn thử này
không thêm Cookie hoặc password/OTP fallback nhằm đo lần xác thực mới. Đây là cấu
hình candidate, chưa phải quyết định cuối cùng cho SSO. Kiểm tra cấu trúc trước khi
tạo client thử, chỉnh policy và thực hiện enrollment. Giữ realm browser binding và
app-lab hiện tại trong lúc chuẩn bị. Không tự gắn required action cho mọi user.

Runtime chưa thay đổi bởi trợ lý. Kết quả SESSION_MAPPING_A giữ 9/19 trong phạm vi
lịch sử; chưa có thêm FR-04–FR-08 được nghiệm thu.
