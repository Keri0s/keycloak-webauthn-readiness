# Các ứng dụng

| Thư mục | Chức năng | Trạng thái |
| --- | --- | --- |
| [readiness](readiness/README.md) | Đọc catalog/phiếu, validation, tính điểm và CLI | Có bộ tests và hồ sơ kiểm chứng logic |
| [lab](lab/README.md) | Django OIDC, danh tính, phiên và logout | Đang triển khai và kiểm chứng từng kịch bản |

Hai phần có dependencies riêng. Readiness không cần Docker hay database để chạy tests. Lab dùng PostgreSQL và Keycloak, không dùng SQLite thay cho bằng chứng lock/concurrency.
