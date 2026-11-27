# Hồ sơ bằng chứng NFR-03 — Dựng lại

- **Yêu cầu (SRS 3.4, NFR-03):** *"README đăng ký passkey, đăng nhập và mở một dòng bằng chứng."*
- **Phương thức kiểm tra theo SRS:** `Demo`
- **Trạng thái hiện tại:** `Đạt demo 3 bước giữa kỳ (còn kiểm chứng máy sạch độc lập)` (ngày `27/11/2026`: đã bổ sung bảng phiên bản công cụ thực dùng và hướng dẫn dựng lab 9 bước từ trạng thái sạch vào `README.md`, đồng thời quay hoàn chỉnh video demo liền mạch 3 bước có thuyết minh tại [`docs/reports/demo_giua_ky_N15.mp4`](../../docs/reports/demo_giua_ky_N15.mp4) (`04:23`, `19.96 MB`) khớp sổ bằng chứng 73 dòng; còn hạng mục chạy kiểm chứng dựng sạch 9 bước trên một máy độc lập thứ hai theo `Chung-01` ở nửa sau)

## Bằng chứng hiện có
- Video demo liền mạch có thuyết minh (27/11/2026): [`docs/reports/demo_giua_ky_N15.mp4`](../../docs/reports/demo_giua_ky_N15.mp4) (`04:23`, `19.96 MB`), trình bày đầy đủ: chấm phiếu lab `27/37` (`FR-01..03`) → đăng ký mới `GK-passkey` (`UPDATE_CREDENTIAL` `36069e0a-bbe8-4373-8e77-be6fdcf28aaa`, `credential_id=5DEAhcI4n2qbsuiHIyONBw` lúc `09:25:04Z`) → đăng nhập passwordless `UV=true` vào `/private/` (`LOGIN` `06e8c39a-a492-4c93-af23-d0d7f65ffac5` lúc `09:25:49Z`, trước đó có ca hủy `513124f1...` lúc `08:56:49Z` `/private/` 403) → `apps.ledger.cli pull --since 2026-11-27` (`added=6`, `total_rows=73`, lúc `09:26:42Z`) và mở dòng bằng chứng bằng `show` / `show --id`.
- Bảng phiên bản công cụ thực dùng và hướng dẫn dựng lab 9 bước từ trạng thái sạch + 3 bước demo tại [`README.md`](../../README.md): chuẩn bị hạ tầng/CA/DB/realm/app → đăng ký passkey (`FR-04`) → đăng nhập `/private/` (`FR-05`) → chạy `apps.ledger.cli pull` và `show --id <evidence_id>` (`FR-06`/`IF-04`).
- Hướng dẫn chi tiết module: [`apps/lab/README.md`](../../apps/lab/README.md), [`apps/ledger/README.md`](../../apps/ledger/README.md), [`infra/README.md`](../../infra/README.md), [`infra/passwordless/README.md`](../../infra/passwordless/README.md).
- Các lượt thực tế ngày 23/11 và 27/11: `5efcdcf3-8031-49c6-be2a-8ccd8f04e425`, `0bf7d697-a7c6-4d95-9e22-f60c2402dd31` ([báo cáo sổ live](../../docs/validation/ledger-2026-11-23/report.md)), cùng các dòng `36069e0a...`, `06e8c39a...`, `513124f1...` trong [`evidence/ledger/so_bang_chung.csv`](../ledger/so_bang_chung.csv).

## Phần còn thiếu / giới hạn
- Quy trình dựng sạch 9 bước mới được hoàn thiện theo cấu hình thực tế ngày 26/11/2026, **chưa được chạy thử lại từ đầu trên một máy sạch độc lập** (dự kiến thực hiện trong kế hoạch tuần 9–10).
- Cần sao chép thêm các ảnh chụp tĩnh đã che dữ liệu phiên từ hội thoại vào thư mục này và `evidence/FR-04..FR-07/` nếu cần nộp kèm hồ sơ ảnh cuối kỳ.

## Ảnh / log người dùng cần tự lưu vào thư mục này
- Ảnh chụp hoặc nhật ký terminal một lượt demo: (1) đăng ký passkey, (2) trang `/private/` sau đăng nhập passkey, (3) lệnh `apps.ledger.cli show --id <evidence_id>` mở đúng 1 dòng bằng chứng.
