# Đối chiếu cấu hình hiện hành — 23/11/2026 13:53 UTC (20:53 UTC+7)

Nguồn: [`inspection.json`](inspection.json) cùng thư mục, do người dùng chạy `.\apps\lab\.venv\Scripts\python.exe .\infra\passwordless\inspect_keycloak.py` (tài khoản `lab-owner`) lúc `2026-11-23T13:53:27.929832+00:00`. Tệp có kích thước 34.545 byte, SHA-256 `28764e84e7b8ef5fa1563e4cc009840fc0c8faef9971288c1a9e748866c3b061`, đã quét FR-08 không có marker (`signals=0`).

Bản ghi này cập nhật cấu hình thực tế sau chuyển đổi passwordless (thay cho mốc preflight ngày 22/11 trước khi gắn flow cho `app-lab`). Đây là kiểm tra cấu hình qua API chỉ đọc; không thay thế các ca kiểm thử hành vi.

| Thành phần | Quan sát từ `inspection.json` | Ghi chú so với mốc 22/11 |
| --- | --- | --- |
| `browser_binding_source` | `client_override` (`app-lab`) | Đã gắn override riêng cho `app-lab` |
| `effective_browser_flow` | `browser-passkey-uv` (`id: 5a254377-...`) | Thay vì `browser-password-webauthn` |
| Executions trong `browser-passkey-uv` | `auth-username-form` (`REQUIRED`), `webauthn-authenticator-passwordless` (`REQUIRED`) | Không có `auth-cookie`, password form hoặc OTP form trong flow này |
| `realm.browserFlow` mặc định toàn realm | `browser-password-webauthn` (trong đó subflow `forms` có `auth-username-password-form` REQUIRED + `webauthn-authenticator` REQUIRED, OTP DISABLED) | Giữ riêng ở mức realm để không ảnh hưởng console/tài khoản khác; `app-lab` dùng override riêng |
| `webAuthnPolicyPasswordlessRpEntityName` / `RpId` | `Readiness Lab` / `auth.readiness.test` | Đã đặt tường minh `auth.readiness.test` (trước đây ở bản preflight 22/11 là rỗng) |
| `webAuthnPolicyPasswordlessSignatureAlgorithms` | `["ES256", "RS256"]` | Giữ nguyên |
| `webAuthnPolicyPasswordlessUserVerificationRequirement` | `required` | UV bắt buộc |
| `webAuthnPolicyPasswordlessAuthenticatorAttachment` | `platform` | Khớp cấu hình platform authenticator |
| `webAuthnPolicyPasswordlessRequireResidentKey` / `PasskeysEnabled` | `"not specified"` / `false` | Ghi nhận theo cấu hình thực tế trả về từ Keycloak |
| `webAuthnPolicyPasswordlessCreateTimeout` | `60` | 60 giây |
| `app-lab` client grants & PKCE | `standardFlowEnabled=true`, `implicitFlowEnabled=false`, `directAccessGrantsEnabled=false`, `serviceAccountsEnabled=false`, `publicClient=false`, `pkce.code.challenge.method=S256` | Không mở grant yếu hoặc implicit |
| `app-lab` redirect & logout URIs | `redirectUris=["https://app.readiness.test:9443/auth/callback/"]`, `post.logout.redirect.uris="https://app.readiness.test:9443/auth/logged-out/"`, `backchannel.logout.url="https://app.readiness.test:9443/auth/backchannel-logout/"` (`backchannel.logout.session.required="true"`) | Đều trỏ về domain lab local (NFR-02) |
| Cấp tài khoản / khôi phục & Events | `registrationAllowed=false`, `resetPasswordAllowed=false`, `rememberMe=false`, `eventsEnabled=true`, `eventsExpiration=604800`, `adminEventsEnabled=false` | Giữ nguyên |

## Giới hạn của bản kiểm kê này

- `inspect_keycloak.py` chỉ đọc allowlist trường realm, client, flows và required actions; chưa đọc danh sách `users`/`credentials` và chưa truy vấn trường `bruteForceProtected` của realm.
- Không kiểm tra client policies, custom providers hoặc hành vi khi nhận assertion `UV=0` (kiểm thử âm UV).
- Chỉ phản ánh cấu hình tại thời điểm `2026-11-23T13:53:27Z`.
