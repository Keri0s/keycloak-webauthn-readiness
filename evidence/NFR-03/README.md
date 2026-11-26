# Hồ sơ bằng chứng NFR-03 — Dựng lại

- **Yêu cầu (SRS 3.4, NFR-03):** *"README đăng ký passkey, đăng nhập và mở một dòng bằng chứng."*
- **Phương thức kiểm tra theo SRS:** `Demo`
- **Trạng thái hiện tại:** `Một phần` (ngày `26/11/2026`: đã bổ sung bảng phiên bản công cụ thực dùng và hướng dẫn dựng lab 9 bước từ trạng thái sạch vào `README.md`, đồng thời đã chạy thực tế bước đăng nhập + kéo/mở dòng bằng chứng trong Mục B–C; còn thiếu chạy kiểm chứng dựng trên máy sạch độc lập và một lượt demo liền mạch từ đăng ký → đăng nhập → mở dòng có lưu ảnh vào thư mục này)

## Bằng chứng hiện có
- Bảng phiên bản công cụ thực dùng và hướng dẫn dựng lab 9 bước từ trạng thái sạch + 3 bước demo tại [`README.md`](../../README.md): chuẩn bị hạ tầng/CA/DB/realm/app → đăng ký passkey (`FR-04`) → đăng nhập `/private/` (`FR-05`) → chạy `apps.ledger.cli pull` và `show --id <evidence_id>` (`FR-06`/`IF-04`).
- Hướng dẫn chi tiết module: [`apps/lab/README.md`](../../apps/lab/README.md), [`apps/ledger/README.md`](../../apps/ledger/README.md), [`infra/README.md`](../../infra/README.md), [`infra/passwordless/README.md`](../../infra/passwordless/README.md).
- Các phần đã thực hiện thực tế ngày 23/11: đăng ký passkey (`09:47`), đăng nhập `/private/` (`18:59:55` và `20:40:42`), kéo sổ và mở chi tiết dòng bằng chứng bằng `show --id 5efcdcf3-8031-49c6-be2a-8ccd8f04e425` và `0bf7d697-a7c6-4d95-9e22-f60c2402dd31` ([báo cáo sổ live](../../docs/validation/ledger-2026-11-23/report.md)).

## Phần còn thiếu / giới hạn
- Quy trình dựng sạch 9 bước mới được hoàn thiện theo cấu hình thực tế ngày 26/11/2026, **chưa được chạy thử lại từ đầu trên một máy sạch độc lập**.
- Cần thực hiện (hoặc ghi nhận trong buổi nghiệm thu) một lượt chạy demo liền mạch từ bước 1 đến bước 3 theo đúng [`README.md`](../../README.md), ghi rõ chỗ làm thủ công (gán required action, nhập PIN, nhập tài khoản admin terminal) và lưu ảnh vào thư mục này.

## Ảnh / log người dùng cần tự lưu vào thư mục này
- Ảnh chụp hoặc nhật ký terminal một lượt demo: (1) đăng ký passkey, (2) trang `/private/` sau đăng nhập passkey, (3) lệnh `apps.ledger.cli show --id <evidence_id>` mở đúng 1 dòng bằng chứng.
