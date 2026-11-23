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

Từ apps/lab, tạo venv, cài dependencies rồi sao chép `.env.example` thành `.env` và tự điền secrets. `DJANGO_SECRET_KEY` phải là chuỗi ngẫu nhiên riêng. Đổi khóa có thể khiến phiên đang đăng nhập cần đăng nhập lại.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Sau khi hoàn tất các điều kiện bên dưới:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:18000
```

Điều kiện hiện chưa được tự động hóa đầy đủ:

- PostgreSQL `readiness_lab` ở 127.0.0.1:15432, role ứng dụng `lab_app` và quyền schema phù hợp. Compose chỉ khởi tạo role admin, không tạo sẵn lab_app.
- Hostnames app.readiness.test/auth.readiness.test trỏ về local; Caddy phục vụ HTTPS cổng 9443. Cấu hình host.docker.internal hiện hướng tới Docker Desktop và Django trên host.
- CA local của Caddy được tin cậy bởi trình duyệt, ứng dụng và Keycloak. Không đưa CA private key lên Git.
- Realm webauthn-lab, confidential client app-lab, callback `/auth/callback/`, post logout `/auth/logged-out/` và backchannel `/auth/backchannel-logout/` được cấu hình đúng origin HTTPS.
- ExternalIdentity phải liên kết issuer/subject với user nội bộ trước khi login. Không tự ghép user theo email.

Xem ma trận `../../tests/fixtures/session-mapping-cases.yaml` và `../../docs/ROADMAP.md`. Hiện thu hồi theo SID đã có kiểm chứng từng phần; subject-wide logout và recovery/cutoff chưa hoàn thành. Chưa có hướng dẫn dựng máy sạch đã được kiểm chứng trọn vẹn.
