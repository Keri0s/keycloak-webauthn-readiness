# Các ứng dụng

| Thư mục | Chức năng | Trạng thái |
| --- | --- | --- |
| [readiness](readiness/README.md) | Đọc catalog/phiếu, validation, tính điểm và CLI | Có bộ tests và hồ sơ kiểm chứng logic |
| [ledger](ledger/README.md) | Kéo Keycloak Admin Events và hiển thị sổ bằng chứng theo allowlist | Có 13 unit test offline PASS và dữ liệu sổ thực 67 dòng |
| [lab](lab/README.md) | Django OIDC, danh tính, phiên và logout | Đang triển khai và kiểm chứng từng kịch bản |

Hai phần có dependencies riêng. Readiness không cần Docker hay database để chạy tests. Lab dùng PostgreSQL và Keycloak, không dùng SQLite thay cho bằng chứng lock/concurrency.
