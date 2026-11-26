# Django authentication lab

## Đối chiếu đăng nhập với trang được bảo vệ

Response HTTP 200 của `/private/` có `X-Lab-Session-Ref`, `X-Lab-Subject-Ref`
và `X-Lab-Binding-Created` sau khi guard xác minh binding. Hai mã đầu là SHA-256
của định danh đã giới hạn scope, không phải cookie/token hoặc quyền truy cập.
[Hướng dẫn thu bằng chứng FR-05](../../docs/validation/requirements-review-2026-11-23/fr05-runbook.md).
Không gửi HAR hoặc Request Headers để đối chiếu. Code mới cần được nạp vào server.

## Callback không hoàn tất (23/11/2026)

Callback bị từ chối sẽ hiện liên kết **Bắt đầu đăng nhập lại** và mã hỗ trợ.
Giao dịch quá 5 phút có thông báo hết thời gian riêng. Giới hạn 5 phút,
kiểm tra state/nonce/PKCE, chữ ký token và binding phiên vẫn giữ nguyên.
Không dùng lại URL callback hoặc URL `login-actions` đã cũ; bắt đầu từ
`https://app.readiness.test:9443/auth/login/`.

Log chẩn đoán nằm ở `apps/lab/.runtime/logs/oidc-callback.log` (đường dẫn
tính từ gốc repository), tự xoay vòng tối đa 3 tệp, mỗi tệp 1 MiB.
Mỗi dòng chỉ có thời gian, mã hỗ trợ, mã lỗi và tên claim từ danh sách cho phép.
Không ghi URL/query, cookie, state, code, token hay nội dung exception.
Log này chẩn đoán callback ứng dụng; không chứng minh nguyên nhân hộp thoại
Windows Security và không thay thế sổ bằng chứng FR-06/FR-07.

Nếu server đang chạy với `--noreload`, dừng đúng terminal Django bằng Ctrl+C
và chạy lại để nạp bản sửa:

```powershell
cd D:\Projects\Do-an-thuctap-totnghiep\apps\lab
.\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:18000 --noreload
```

Kiểm thử hồi quy offline (không kết nối Keycloak hoặc tạo database):

```powershell
.\.venv\Scripts\python.exe manage.py test authn.test_oidc_recovery --verbosity 2
```

Các kiểm thử này không kiểm tra Windows Hello hoặc passkey thật.

## Các module đã xây dựng

| File/thư mục | Trách nhiệm |
| --- | --- |
| manage.py | Điểm vào lệnh Django |
| config/settings.py | Database, cookie Secure/HttpOnly, proxy HTTPS, OIDC và logging |
| config/oidc.py | Authlib client; ràng buộc issuer, state, nonce, PKCE và claims |
| config/urls.py | Routing trang bảo vệ, callback và logout |
| config/asgi.py, wsgi.py | Điểm vào máy chủ ứng dụng |
| authn/models.py | ExternalIdentity, OIDCSessionGroup, SessionBinding, SIDRevocationMarker, LogoutReceipt |
| authn/services.py | Tra danh tính, tạo binding, thu hồi SID và xử lý receipt trong giao dịch |
| authn/transactions.py | PostgreSQL advisory lock theo issuer/client để đồng bộ thao tác phiên |
| authn/permissions.py | Chặn truy cập nếu binding, danh tính hoặc backend session không hợp lệ |
| authn/backchannel.py | Xác minh chữ ký/claims logout token theo profile yêu cầu SID |
| authn/views.py | Luồng HTTP login/callback/private/logout/backchannel |
| authn/migrations/0001–0005 | Lịch sử tạo schema; cần giữ trong Git để migrate |
| authn/templates/authn/private.html | Trang minh họa danh tính và nút đăng xuất |
| authn/tests.py | File khung, không đại diện bộ 19 kịch bản; xem tests/ và tmp/ |
| requirements.txt | Phiên bản dependencies của lab |
| .env.example | Tên biến cần thiết, không chứa giá trị bí mật |

## Chuẩn bị môi trường

Xem quy trình dựng đầy đủ 9 bước từ trạng thái sạch tại [README gốc](../../README.md#hướng-dẫn-dựng-lab-từ-trạng-thái-sạch-clean-setup). Từ `apps/lab`, tạo `.venv`, cài dependencies đúng phiên bản (`Django==5.2.19`, `Authlib==1.9.6`, `requests==2.34.2`, `psycopg[binary]==3.3.9`, `python-dotenv==1.2.4`), sao chép `.env.example` thành `.env` và tự điền secrets. `DJANGO_SECRET_KEY` phải là chuỗi ngẫu nhiên riêng. Đổi khóa có thể khiến phiên đang đăng nhập cần đăng nhập lại.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Sau khi hoàn tất các điều kiện hạ tầng bên dưới:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
# Liên kết ExternalIdentity (không dùng mật khẩu nội bộ) rồi chạy dev server:
.\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:18000 --noreload
```

Điều kiện hạ tầng cần chuẩn bị trước khi migrate/chạy (chưa tự động hóa):

- PostgreSQL `readiness_lab` ở `127.0.0.1:15432` đã có role ứng dụng `lab_app` (`Compose` chỉ tạo sẵn `lab_db_admin`); trên PostgreSQL 17 cần cấp tường minh `GRANT CONNECT ON DATABASE readiness_lab TO lab_app;` và `GRANT USAGE, CREATE ON SCHEMA public TO lab_app;` để `manage.py migrate` chạy được.
- Hostnames `app.readiness.test` và `auth.readiness.test` trỏ về `127.0.0.1`; Caddy phục vụ HTTPS cổng `9443`. Cấu hình `host.docker.internal` hướng tới Docker Desktop và Django chạy trên host cổng `18000`.
- CA local của Caddy (`infra/.runtime/caddy-data/caddy/pki/authorities/local/root.crt`, dùng trực tiếp bởi `OIDC_CA_BUNDLE` trong `config/settings.py`) được cài tin cậy trên Windows/trình duyệt và chứng chỉ công khai đã sao chép sang `infra/.runtime/keycloak-trust/readiness-root.pem`. Không đưa CA private key lên Git.
- Realm `webauthn-lab`, flow `browser-passkey-uv` (`auth-username-form` + `webauthn-authenticator-passwordless`), WebAuthn Passwordless Policy (`RP ID=auth.readiness.test`, `UV=required`), confidential client `app-lab` (PKCE `S256`, Browser Flow override `browser-passkey-uv`, callback `/auth/callback/`, post logout `/auth/logged-out/` và backchannel `/auth/backchannel-logout/`) được cấu hình đúng origin HTTPS.
- `ExternalIdentity` phải liên kết `(issuer, sub)` với user nội bộ `lab-user-01` (không có mật khẩu nội bộ) trước khi login; tham khảo mẫu tại `../../tmp/link_lab_user.py`. Không tự ghép user theo email.

Xem ma trận `../../tests/fixtures/session-mapping-cases.yaml` và `../../docs/ROADMAP.md`. Hiện thu hồi theo SID đã có kiểm chứng từng phần; subject-wide logout và recovery/cutoff chưa hoàn thành. Quy trình dựng sạch đã được viết chi tiết từ cấu hình hiện hành ngày `26/11/2026`, nhưng **chưa được kiểm chứng lặp lại trên một máy sạch độc lập**.
