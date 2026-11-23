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

Compose dùng Caddy 2.11.9 và PostgreSQL 17.12. Đây là phiên bản ghi trong cấu hình repository, không phải cam kết bản mới nhất.

Sao chép .env.example sang .env và điền secrets riêng. Cấu hình hiện tại cần CA public tại `.runtime/keycloak-trust/readiness-root.pem` trước khi Keycloak chạy; file phải đọc được từ container. Caddy tạo CA trong runtime của nó. Quy trình bootstrap CA, tài khoản quản trị Keycloak, realm/client và role lab_app chưa được tự động hóa hoàn chỉnh. Không coi `docker compose up` trên máy sạch là quy trình đã kiểm chứng.

Sau khi chuẩn bị, chạy từ thư mục infra:

```powershell
docker compose up -d
docker compose ps
```

Ứng dụng Django chạy trên host, xem [hướng dẫn lab](../apps/lab/README.md). File realm trong dữ liệu mẫu không phải bản export cấu hình runtime đã nghiệm thu. Không dùng môi trường, volume hoặc credential của hệ thống khác.
