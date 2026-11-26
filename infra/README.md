# Hạ tầng lab local

Chuẩn bị chuyển passwordless: [hướng dẫn và công cụ kiểm kê](passwordless/README.md).
Công cụ đọc cấu hình qua HTTPS; chưa tự thay flow/policy của Keycloak.

| Thành phần | Chức năng |
| --- | --- |
| compose.yaml / caddy | Reverse proxy HTTPS trên 127.0.0.1:9443 |
| compose.yaml / keycloak | Identity provider Keycloak 26.8.2 |
| compose.yaml / keycloak-db | PostgreSQL riêng cho Keycloak |
| compose.yaml / app-db | PostgreSQL readiness_lab, cổng host 15432 |
| Caddyfile | auth.readiness.test đến Keycloak; app.readiness.test đến Django host:18000 |
| .env.example | Biến mật khẩu cần điền trên máy local |
| .runtime/ (không commit) | Database, CA và dữ liệu dịch vụ sinh khi chạy |

Compose dùng Caddy `2.11.9` (`caddy:2.11.9-alpine`, Alpine Linux `3.24.4`), Keycloak `26.8.2` (`quay.io/keycloak/keycloak:26.8.2`, RHEL `9.9`) và PostgreSQL `17.12` (`postgres:17.12-bookworm`, Debian `12`). Đây là phiên bản thực tế được khai báo và đối chiếu trong repository tính đến `26/11/2026`.

Xem quy trình dựng đầy đủ 9 bước từ trạng thái sạch tại [README gốc](../README.md#hướng-dẫn-dựng-lab-từ-trạng-thái-sạch-clean-setup). Tóm tắt thứ tự bắt buộc trên máy mới:

1. Sao chép `.env.example` sang `.env` và điền hai mật khẩu riêng (`KEYCLOAK_DB_PASSWORD`, `LAB_DB_ADMIN_PASSWORD`).
2. Khởi chạy `caddy` **trước** (`docker compose up -d caddy`) để sinh CA nội bộ tại `.runtime/caddy-data/caddy/pki/authorities/local/root.crt`, rồi sao chép **chứng chỉ công khai** sang `.runtime/keycloak-trust/readiness-root.pem` và cài `root.crt` vào Trusted Root CA của Windows. Không chạy `docker compose up -d` toàn bộ trước bước này để tránh Docker tạo nhầm thư mục rỗng tại đường dẫn mount file của Keycloak.
3. Khởi động hai PostgreSQL (`docker compose up -d keycloak-db app-db`), tạo tài khoản quản trị tạm cho Keycloak 26.8.2 bằng `docker compose run --rm keycloak bootstrap-admin user` trên DB trống, sau đó mới chạy `docker compose up -d keycloak`.
4. Tạo role `lab_app` trong `app-db` (`CREATE ROLE lab_app ...`, cấp `CONNECT ON DATABASE readiness_lab` và `USAGE, CREATE ON SCHEMA public`), rồi cấu hình realm `webauthn-lab`, policy passwordless, flow `browser-passkey-uv` và client `app-lab`.

Quy trình bootstrap CA, tài khoản quản trị Keycloak, realm/client và role `lab_app` chưa được tự động hóa và **chưa được chạy kiểm chứng lặp lại trên một máy sạch độc lập**.

Sau khi chuẩn bị đầy đủ, chạy hàng ngày từ thư mục `infra/`:

```powershell
docker compose up -d
docker compose ps
```

Ứng dụng Django chạy trên host, xem [hướng dẫn lab](../apps/lab/README.md). File realm trong dữ liệu mẫu không phải bản export cấu hình runtime đã nghiệm thu. Không dùng môi trường, volume hoặc credential của hệ thống khác.
