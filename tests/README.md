# Kiểm thử

| File | Vai trò |
| --- | --- |
| test_fr01_catalog.py | Kiểm tra catalog tiêu chí |
| test_fr02_validation.py | Kiểm tra dữ liệu và miền điểm |
| test_fr03_calculator.py | Tổng điểm, thiếu dữ liệu |
| test_readiness_regressions.py | Ca hồi quy readiness |
| fixtures/session-mapping-cases.yaml | Đặc tả 19 ca lá quản lý phiên và kết quả từng ca |

Chạy `python -m pytest tests -q` từ gốc cho readiness. Lệnh này không tự chạy 19 ca lab. Các script lab nằm ở [tmp/](../tmp/README.md), cần PostgreSQL và cấu hình lab, tạo/xóa dữ liệu tổng hợp. Không chạy với Python -O vì script dùng assert.

Ma trận hiện ghi 9/19 PASS. Các đường dẫn design_reference nội bộ trong YAML được giữ để truy vết; phần public tóm tắt ở docs/ROADMAP.md và apps/lab/README.md. Chưa có runner tự động diễn giải toàn YAML.
