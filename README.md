# Keycloak WebAuthn Readiness

Đồ án xây dựng bộ đánh giá mức sẵn sàng an ninh và lab kiểm chứng xác thực, quản lý phiên với Keycloak, Django và PostgreSQL. Tác giả: Trần Trung Hiếu.

## Trạng thái ngày 18/11/2026

| Thành phần | Đã làm | Phần còn lại |
| --- | --- | --- |
| Readiness engine | Nạp YAML/CSV, kiểm tra dữ liệu, tính điểm, CLI; hồ sơ 81 tests PASS ngày 13/11 | Đưa bằng chứng đo từ lab vào phiếu thay cho dữ liệu mẫu |
| Lab OIDC | Cấu hình Compose/Caddy, callback, liên kết danh tính, cookie phiên và logout | Hoàn thiện hướng dẫn dựng máy sạch; kiểm chứng thêm giao thức và vận hành |
| Quản lý phiên | Group theo issuer/client/SID, binding Django session, marker thu hồi, receipt chống xử lý lặp, transaction lock | 10 ca còn lại trong ma trận 19 ca; các quyết định thu hồi theo subject |
| Kiểm chứng phiên | 9/19 ca ghi PASS, một số fault injection đã chạy | Mở rộng coverage; concurrency và thử nghiệm Keycloak thật |
| Sổ sự kiện, bằng chứng WebAuthn | Có dữ liệu và hồ sơ mẫu | Thu thập sự kiện thực, thử hủy xác thực, kiểm chứng không lộ private key và nghiệm thu |

PASS hiện có chỉ áp dụng cho phạm vi từng bài kiểm thử. 81 tests readiness và 19 kịch bản phiên là hai bộ khác nhau. Điểm 29/37 là kết quả fixture, không phải điểm an ninh của lab. Đây là đồ án đang phát triển, chưa phải bản triển khai production đã nghiệm thu.

## Đọc repository từ đâu?

| File/thư mục | Vai trò |
| --- | --- |
| [apps/](apps/README.md) | Hai phần ứng dụng readiness và lab |
| [apps/readiness/](apps/readiness/README.md) | Models, loader, parser, evaluator và CLI tính điểm |
| [apps/lab/](apps/lab/README.md) | Django app OIDC và ánh xạ phiên; có chú thích từng module |
| [infra/](infra/README.md) | Docker Compose cho hai database, Keycloak và Caddy |
| [tests/](tests/README.md) | Tests readiness và ma trận kịch bản phiên |
| [tmp/](tmp/README.md) | Các script thực nghiệm được chọn để tái lập kết quả lab |
| [docs/](docs/README.md) | Chỉ mục bằng chứng và kế hoạch công việc tiếp theo |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Đã làm, chưa làm, ưu tiên tiếp theo và giới hạn |
| [docs/validation/](docs/validation/README.md) | Báo cáo, kết quả máy đọc được và hash nguồn tại thời điểm chạy |
| [DU_LIEU_MAU/N15_San_sang_WebAuthn/](DU_LIEU_MAU/N15_San_sang_WebAuthn/README.md) | Catalog 16 tiêu chí, CSV và realm mẫu tổng hợp |
| [evidence/](evidence/README.md) | Hồ sơ mẫu theo CH/VA/XT/NK, chưa phải nghiệm thu lab |
| requirements.txt | Dependencies cho readiness/tests; lab có requirements riêng |
| .gitignore | Loại secrets, runtime, DB, môi trường Python và tài liệu nội bộ |

## Chạy readiness

Từ thư mục gốc, dùng Python 3.12 trong môi trường ảo:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests -q
python -m apps.readiness.cli --scorecard DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_mau_day_du.csv --evaluator "Nguoi cham lab"
```

CLI nhận phiếu CSV và catalog YAML; ô chưa chấm khác điểm 0. Bộ mẫu có 16 tiêu chí, tổng tối đa 37. Chi tiết quy tắc nằm trong README của readiness.

## Chạy lab

Xem [apps/lab/README.md](apps/lab/README.md) và [infra/README.md](infra/README.md). Lab cần cấu hình realm/client, CA tin cậy, role database và danh tính đã liên kết. Clone repository rồi chạy Compose chưa đủ để tái tạo toàn bộ môi trường.

Bản public không chứa `.env`, khóa riêng, CA runtime, dữ liệu PostgreSQL, cookie, token hoặc tài khoản thật. Chỉ dùng lab local với dữ liệu tổng hợp. SRS là tài liệu định hướng học thuật; phạm vi nghiệm thu cuối cùng còn cần được xác nhận. Các tài liệu bàn giao và trao đổi nội bộ không nằm trong bản public.
